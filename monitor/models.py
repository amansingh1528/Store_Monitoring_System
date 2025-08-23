from django.db import models
import uuid

class Store(models.Model):
    id = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return f"Store({self.id})"


class StoreStatus(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='statuses')
    timestamp_utc = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'timestamp_utc']),
        ]


class BusinessHours(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='bizhours')
    day_of_week = models.IntegerField(db_index=True)
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

    class Meta:
        indexes = [
            models.Index(fields=['store', 'day_of_week']),
        ]


class StoreTimezone(models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name='tz')
    timezone_str = models.CharField(max_length=64, default='America/Chicago')


class Report(models.Model):
    class Status(models.TextChoices):
        RUNNING = 'RUNNING', 'Running'
        COMPLETE = 'COMPLETE', 'Complete'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.RUNNING)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    reference_utc = models.DateTimeField(null=True, blank=True)
    csv_path = models.CharField(max_length=512, null=True, blank=True)
    error = models.TextField(null=True, blank=True)


class ReportRow(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='rows')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    uptime_last_hour_m = models.IntegerField()
    uptime_last_day_h = models.FloatField()
    uptime_last_week_h = models.FloatField()
    downtime_last_hour_m = models.IntegerField()
    downtime_last_day_h = models.FloatField()
    downtime_last_week_h = models.FloatField()

    class Meta:
        unique_together = ('report', 'store')
        indexes = [
            models.Index(fields=['report', 'store']),
        ]
