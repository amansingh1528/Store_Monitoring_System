import os
import pandas as pd
from django.core.management.base import BaseCommand
from monitor.models import Store, StoreStatus, BusinessHours, StoreTimezone
from zipfile import ZipFile
from django.db import transaction
from datetime import datetime, timezone
class Command(BaseCommand):
    help = 'Load store monitoring data from zip file'

    def add_arguments(self, parser):
        parser.add_argument('--zip', required=True, help='Path to zip file')

    def handle(self, *args, **options):
        zip_path = options['zip']
        extract_dir = os.path.expanduser('/Users/mac/Desktop/temp2')


        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)


        stores_df = pd.read_csv(os.path.join(extract_dir, 'store_status.csv'))
        bh_df = pd.read_csv(os.path.join(extract_dir, 'menu_hours.csv'))
        tz_df = pd.read_csv(os.path.join(extract_dir, 'timezones.csv'))


        store_ids = set(stores_df['store_id']).union(bh_df['store_id']).union(tz_df['store_id'])
        store_objs = [Store(id=sid) for sid in store_ids]


        Store.objects.bulk_create(store_objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Inserted {len(store_ids)} stores'))


        bh_objs = [
            BusinessHours(
                store_id=row['store_id'],
                day_of_week=row.get('day', row.get('day_of_week')),
                start_time_local=row['start_time_local'],
                end_time_local=row['end_time_local']
            )
            for _, row in bh_df.iterrows()
        ]


        tz_objs = [
            StoreTimezone(
                store_id=row['store_id'],
                timezone_str=row['timezone_str']
            )
            for _, row in tz_df.iterrows()
        ]


        '''
        status_objs = [
            StoreStatus(
                store_id=row['store_id'],
                timestamp_utc=row['timestamp_utc'],
                status=row['status']
            )
            for _, row in stores_df.iterrows()
        ]'''
        status_objs = [
            StoreStatus(
                store_id=row['store_id'],
                timestamp_utc=datetime.strptime(row['timestamp_utc'].replace(' UTC', ''), "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc),
                status=row['status']
            )
            for _, row in stores_df.iterrows()
        ]




        batch_size = 1000
        for model_objs, model in [
            (bh_objs, BusinessHours),
            (tz_objs, StoreTimezone),
            (status_objs, StoreStatus),
        ]:
            for i in range(0, len(model_objs), batch_size):
                model.objects.bulk_create(model_objs[i:i+batch_size], ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS(f'Inserted {min(i+batch_size, len(model_objs))}/{len(model_objs)} {model.__name__}'))

        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))
