import pandas as pd
from datetime import datetime, timedelta, time
import pytz
from .models import StoreStatus, BusinessHours, StoreTimezone

DEFAULT_TZ = "America/Chicago"

def get_timezone(store_id):
    try:
        return StoreTimezone.objects.get(store_id=store_id).timezone_str
    except StoreTimezone.DoesNotExist:
        return DEFAULT_TZ

def get_business_hours(store_id):

    hours = list(BusinessHours.objects.filter(store_id=store_id))
    if not hours:
        return None

    biz_map = {}
    for h in hours:
        biz_map.setdefault(h.day_of_week, []).append((h.start_time_local, h.end_time_local))
    return biz_map

def localize_utc_to_store(utc_dt, tz_str):
    tz = pytz.timezone(tz_str)
    return utc_dt.astimezone(tz)

def compute_uptime_for_intervals(store_id, reference_utc):


    tz_str = get_timezone(store_id)
    store_tz = pytz.timezone(tz_str)


    last_hour_start = reference_utc - timedelta(hours=1)
    last_day_start = reference_utc - timedelta(days=1)
    last_week_start = reference_utc - timedelta(days=7)


    qs = StoreStatus.objects.filter(store_id=store_id, timestamp_utc__gte=last_week_start).order_by('timestamp_utc')
    records = list(qs)

    if not records:
        return (0, 0, 0, 60, 24, 24 * 7)


    biz_map = get_business_hours(store_id)


    intervals = []
    prev_ts = last_week_start
    prev_status = records[0].status
    for rec in records:
        intervals.append((prev_ts, rec.timestamp_utc, prev_status))
        prev_ts = rec.timestamp_utc
        prev_status = rec.status
    intervals.append((prev_ts, reference_utc, prev_status))


    def accumulate(start, end):
        up = 0
        down = 0

        cur = start
        while cur < end:
            chunk_end = min(end, cur + timedelta(minutes=15))
            loc_cur = cur.astimezone(store_tz)
            dow = loc_cur.weekday()
            if biz_map:

                in_hours = False
                for s, e in biz_map.get(dow, []):
                    if s <= loc_cur.timetz() < e:
                        in_hours = True
                        break
                if not in_hours:
                    return 0, 0
            mins = (chunk_end - cur).total_seconds() / 60
            return (mins, 0) if status == 'active' else (0, mins)


    uptime_last_hour = downtime_last_hour = 0
    uptime_last_day = downtime_last_day = 0
    uptime_last_week = downtime_last_week = 0

    for start, end, status in intervals:
        if end <= last_hour_start:
            pass
        elif start < reference_utc:
            effective_start = max(start, last_week_start)
            effective_end = min(end, reference_utc)
            up, down = distribute_time(effective_start, effective_end, status, store_tz, biz_map)
            uptime_last_week += up
            downtime_last_week += down
            if effective_end > last_day_start:
                up_day, down_day = distribute_time(max(effective_start, last_day_start), effective_end, status, store_tz, biz_map)
                uptime_last_day += up_day
                downtime_last_day += down_day
            if effective_end > last_hour_start:
                up_hr, down_hr = distribute_time(max(effective_start, last_hour_start), effective_end, status, store_tz, biz_map)
                uptime_last_hour += up_hr
                downtime_last_hour += down_hr


    return (
        int(round(uptime_last_hour)), round(uptime_last_day / 60, 2), round(uptime_last_week / 60, 2),
        int(round(downtime_last_hour)), round(downtime_last_day / 60, 2), round(downtime_last_week / 60, 2)
    )

def distribute_time(start, end, status, store_tz, biz_map):

    total_up = 0
    total_down = 0
    current = start
    while current < end:
        next_point = min(end, current + timedelta(minutes=5))
        loc = current.astimezone(store_tz)
        dow = loc.weekday()
        if biz_map:
            in_hours = False
            for s, e in biz_map.get(dow, []):
                if s <= loc.timetz() < e:
                    in_hours = True
                    break
            if not in_hours:
                current = next_point
                continue
        mins = (next_point - current).total_seconds() / 60
        if status == 'active':
            total_up += mins
        else:
            total_down += mins
        current = next_point
    return total_up, total_down
