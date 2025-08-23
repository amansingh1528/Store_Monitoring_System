import threading
import csv
import os
from django.utils import timezone
from .models import Report, Store
from .utils import compute_uptime_for_intervals

def generate_report_async(report_id):
    thread = threading.Thread(target=_generate_report, args=(report_id,))
    thread.start()

def _generate_report(report_id):
    try:
        report = Report.objects.get(id=report_id)
        report.started_at = timezone.now()
        # Reference UTC timestamp = max timestamp from StoreStatus
        from .models import StoreStatus
        max_ts = StoreStatus.objects.order_by('-timestamp_utc').first().timestamp_utc
        report.reference_utc = max_ts
        report.save()


        media_dir = os.path.join(os.getcwd(), 'media')
        os.makedirs(media_dir, exist_ok=True)
        csv_path = os.path.join(media_dir, f'report_{report_id}.csv')

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'store_id', 'uptime_last_hour(in minutes)', 'uptime_last_day(in hours)',
                'uptime_last_week(in hours)', 'downtime_last_hour(in minutes)',
                'downtime_last_day(in hours)', 'downtime_last_week(in hours)'
            ])

            for store in Store.objects.all():
                row = compute_uptime_for_intervals(store.id, max_ts)
                writer.writerow([store.id] + list(row))

        report.status = Report.Status.COMPLETE
        report.finished_at = timezone.now()
        report.csv_path = csv_path
        report.save()
    except Exception as e:
        report.status = Report.Status.FAILED
        report.error = str(e)
        report.finished_at = timezone.now()
        report.save()
