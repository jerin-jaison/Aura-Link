"""
Plan model for subscription tiers.
"""

from django.db import models
from django.contrib.postgres.fields import JSONField


class Plan(models.Model):
    """Subscription plan model."""
    
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_videos = models.IntegerField(null=True, blank=True, help_text="NULL = unlimited")
    cloud_upload_allowed = models.BooleanField(default=False)
    playlist_loop_allowed = models.BooleanField(default=False)
    
    # Staff-specific fields
    max_clients = models.IntegerField(null=True, blank=True, help_text="Max client devices for staff plans. NULL for regular plans")
    max_storage_gb = models.IntegerField(null=True, blank=True, help_text="Max storage in GB for staff plans")
    is_staff_plan = models.BooleanField(default=False, help_text="Is this a staff/business plan?")
    
    features = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'plans'
        ordering = ['price']
    
    def __str__(self):
        return self.name