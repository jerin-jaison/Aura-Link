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
    
    # Display settings
    rotation = models.IntegerField(
        default=0,
        choices=[(0, '0°'), (90, '90°'), (180, '180°'), (270, '270°')],
        help_text='Video rotation angle for display'
    )
    
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


# ============================================================================
# Staff Video Assignment Model
# ============================================================================

class StaffVideoAssignment(models.Model):
    """Maps staff-uploaded videos to client devices."""
    
    video = models.ForeignKey(
        'Video',
        on_delete=models.CASCADE,
        related_name='staff_assignments'
    )
    
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='video_assignments',
        limit_choices_to={'user_type': 'STAFF'}
    )
    
    # Assignment scope
    assigned_to = models.ForeignKey(
        'accounts.ClientAccount',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='video_assignments',
        help_text="Specific client. NULL if global for all staff clients"
    )
    
    is_global_for_staff = models.BooleanField(
        default=False,
        help_text="Show to all clients of this staff"
    )
    
    # Playback settings
    play_order = models.IntegerField(default=0, help_text="Order in playlist (lower plays first)")
    loop_enabled = models.BooleanField(default=True, help_text="Loop this video")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'staff_video_assignments'
        verbose_name = 'Staff Video Assignment'
        verbose_name_plural = 'Staff Video Assignments'
        ordering = ['play_order', '-created_at']
        indexes = [
            models.Index(fields=['staff', 'play_order']),
            models.Index(fields=['assigned_to', 'play_order']),
        ]
        # Prevent duplicate assignments
        unique_together = [['video', 'assigned_to']]
    
    def __str__(self):
        if self.assigned_to:
            return f"{self.video.title} → {self.assigned_to.device_name}"
        elif self.is_global_for_staff:
            return f"{self.video.title} → All clients of {self.staff.email}"
        return f"{self.video.title} (Unassigned)"
    
    def save(self, *args, **kwargs):
        # Ensure video owner is the staff member
        if self.video.owner != self.staff:
            raise ValueError("Video must be owned by the staff member")
        
        # If global, assigned_to must be NULL
        if self.is_global_for_staff and self.assigned_to:
            raise ValueError("Global assignments cannot target specific clients")
        
        super().save(*args, **kwargs)