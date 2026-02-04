"""
Periodic tasks for subscription management.
"""

from celery import shared_task
from apps.subscriptions.models import Subscription
from apps.plans.models import Plan
from django.utils import timezone


@shared_task
def check_expired_subscriptions():
    """Check and update expired subscriptions."""
    
    now = timezone.now()
    expired_count = 0
    downgraded_count = 0
    
    for subscription in Subscription.objects.filter(status='ACTIVE'):
        if subscription.end_date < now:
            if subscription.is_in_grace_period():
                subscription.status = 'IN_GRACE_PERIOD'
                subscription.save()
                expired_count += 1
            elif subscription.should_downgrade():
                # Downgrade to Free plan
                free_plan = Plan.objects.get(name='Free')
                subscription.user.plan = free_plan
                subscription.user.save()
                subscription.status = 'EXPIRED'
                subscription.save()
                downgraded_count += 1
    
    return f"Expired: {expired_count}, Downgraded: {downgraded_count}"