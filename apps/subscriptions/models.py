"""
Subscription model with lifecycle management.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Subscription(models.Model):
    """Subscription model with grace period logic."""
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('IN_GRACE_PERIOD', 'In Grace Period'),
        ('CANCELLED', 'Cancelled'),
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey('plans.Plan', on_delete=models.SET_NULL, null=True)
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    grace_period_days = models.IntegerField(default=7)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name if self.plan else 'No Plan'}"
    
    def is_in_grace_period(self):
        """Check if subscription is in grace period."""
        if self.end_date < timezone.now():
            grace_end = self.end_date + timedelta(days=self.grace_period_days)
            return timezone.now() <= grace_end
        return False
    
    def should_downgrade(self):
        """Check if subscription should be downgraded."""
        if self.end_date < timezone.now():
            grace_end = self.end_date + timedelta(days=self.grace_period_days)
            return timezone.now() > grace_end
        return False
    
    def days_until_expiry(self):
        """Get days until expiration."""
        if self.end_date > timezone.now():
            delta = self.end_date - timezone.now()
            return delta.days
        return 0