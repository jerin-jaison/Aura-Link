"""
Audit logging for admin actions.
"""

from django.db import models
from django.conf import settings


class AdminActionLog(models.Model):
    """Log all administrative actions."""
    
    ACTION_CHOICES = (
        ('USER_CREATED', 'User Created'),
        ('USER_DELETED', 'User Deleted'),
        ('USER_BLOCKED', 'User Blocked'),
        ('PLAN_CHANGED', 'Plan Changed'),
        ('VIDEO_DISABLED', 'Video Disabled'),
        ('VIDEO_ACTIVATED', 'Video Activated'),
        ('VIDEO_ARCHIVED', 'Video Archived'),
        ('VIDEO_DELETED', 'Video Deleted'),
        ('FEATURE_TOGGLED', 'Feature Toggled'),
        ('DELETION_REQUESTED', 'Deletion Requested'),
        ('DELETION_APPROVED', 'Deletion Approved'),
        ('DELETION_REJECTED', 'Deletion Rejected'),
    )
    
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_model = models.CharField(max_length=50)
    target_id = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_action_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action_type']),
        ]
    
    def __str__(self):
        return f"{self.action_type} by {self.admin.email if self.admin else 'Unknown'}"