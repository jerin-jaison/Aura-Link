"""
Video model with validation and storage management.
"""

import uuid
from django.db import models
from django.conf import settings


class Video(models.Model):
    """Video model with plan-based constraints."""
    
    STORAGE_CHOICES = (
        ('LOCAL', 'Local Filesystem'),
        ('CLOUD', 'Cloud Storage'),
    )
    
    FORMAT_CHOICES = (
        ('mp4', 'MP4'),
        ('mkv', 'MKV'),
        ('webm', 'WebM'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    
    title = models.CharField(max_length=255)
    storage_type = models.CharField(max_length=10, choices=STORAGE_CHOICES, default='LOCAL')
    file_path = models.CharField(max_length=500, blank=True)
    cloud_url = models.URLField(max_length=1000, blank=True)
    
    # File metadata
    file_size = models.BigIntegerField(default=0, help_text='Size in bytes')
    duration = models.IntegerField(default=0, help_text='Duration in seconds')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='mp4')
    thumbnail_url = models.URLField(max_length=1000, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False, help_text="Visible to all users")
    uploaded_by_admin = models.BooleanField(default=False, help_text="Uploaded by admin, requires approval to delete")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'videos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.owner.email})"
    
    @property
    def file_size_mb(self):
        """Get file size in MB."""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def duration_minutes(self):
        """Get duration in minutes."""
        return round(self.duration / 60, 2)

    @property
    def get_file_url(self):
        """Get video file URL."""
        if self.storage_type == 'CLOUD':
            return self.cloud_url
        return f"{settings.MEDIA_URL}videos/{self.file_path}"
    
    def can_be_deleted_by_user(self, user):
        """Check if a user can delete this video."""
        # Admins can delete any video
        if user.is_admin:
            return True
        # Users can only delete their own videos that weren't uploaded by admin and aren't global
        if self.owner == user and not self.uploaded_by_admin and not self.is_global:
            return True
        return False
    
    def requires_deletion_approval(self):
        """Check if this video requires admin approval for deletion."""
        return self.uploaded_by_admin or self.is_global