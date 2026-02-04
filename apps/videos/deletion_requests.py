"""
Video deletion request model for admin-uploaded videos.
"""

import uuid
from django.db import models
from django.conf import settings


class VideoDeletionRequest(models.Model):
    """Track user requests to delete admin-uploaded videos."""
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(
        'videos.Video',
        on_delete=models.CASCADE,
        related_name='deletion_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deletion_requests'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField(blank=True, help_text="User's reason for deletion request")
    admin_notes = models.TextField(blank=True, help_text="Admin notes for approval/rejection")
    
    # Admin who resolved the request
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_deletion_requests'
    )
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'video_deletion_requests'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status', '-requested_at']),
        ]
    
    def __str__(self):
        return f"Deletion request for {self.video.title} by {self.requested_by.email}"
