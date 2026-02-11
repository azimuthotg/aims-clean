from django.db import models
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
