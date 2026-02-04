"""
Cleanup and maintenance tasks.
"""

from celery import shared_task
from apps.audit.models import AdminActionLog
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


@shared_task
def cleanup_audit_logs():
    """Delete old audit logs."""
    
    retention_days = settings.AUDIT_LOG_RETENTION_DAYS
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    
    deleted_count, _ = AdminActionLog.objects.filter(
        timestamp__lt=cutoff_date
    ).delete()
    
    return f"Deleted {deleted_count} old audit logs"