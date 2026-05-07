from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class PushSubscription(models.Model):
    """Model to store push notification subscriptions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh_key = models.CharField(max_length=200)
    auth_key = models.CharField(max_length=200)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'push_subscriptions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['endpoint']),
        ]
    
    def __str__(self):
        return f"Push subscription for {self.user.username} ({self.endpoint[:50]}...)"


class SyncLog(models.Model):
    TABLE_CHOICES = [
        ('staff_info', 'ข้อมูลบุคลากร (staff_info)'),
        ('students_info', 'ข้อมูลนักศึกษา (students_info)'),
    ]
    STATUS_CHOICES = [
        ('running', 'กำลังดำเนินการ'),
        ('success', 'สำเร็จ'),
        ('failed', 'ล้มเหลว'),
    ]

    table_name = models.CharField(max_length=50, choices=TABLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    records_before = models.IntegerField(default=0)
    records_after = models.IntegerField(default=0)
    records_synced = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, default='')
    triggered_by = models.CharField(max_length=20, default='manual')  # 'manual' | 'schedule'
    triggered_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='sync_logs'
    )

    class Meta:
        db_table = 'sync_logs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['table_name', 'started_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"SyncLog [{self.table_name}] {self.status} @ {self.started_at}"

    @property
    def duration_seconds(self):
        if self.finished_at:
            return round((self.finished_at - self.started_at).total_seconds(), 1)
        return None
