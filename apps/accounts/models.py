"""
Custom User model for Aura Link.
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with UUID primary key."""
    
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('USER', 'Regular User'),
    )
    
    USER_TYPE_CHOICES = (
        ('REGULAR', 'Regular User'),
        ('STAFF', 'Staff Member'),
        ('CLIENT', 'Client Device'),
        ('ADMIN', 'Administrator'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, unique=True, blank=True, null=True, db_index=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='REGULAR', db_index=True)
    plan = models.ForeignKey('plans.Plan', on_delete=models.SET_NULL, null=True, related_name='users')
    
    # User status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        # Auto-generate username from email if not provided
        if not self.username:
            self.username = self.email.split('@')[0]
        
        # Admin users are always staff
        if self.role == 'ADMIN':
            self.is_staff = True
            
        super().save(*args, **kwargs)
    
    @property
    def is_admin(self):
        """Check if user is an administrator."""
        return self.role == 'ADMIN'
    
    @property
    def is_staff_member(self):
        """Check if user is a staff member (not Django is_staff)."""
        return self.user_type == 'STAFF'
    
    @property
    def is_client(self):
        """Check if user is a client device."""
        return self.user_type == 'CLIENT'
    
    @property
    def total_videos(self):
        """Get total number of videos uploaded by user."""
        return self.videos.filter(is_active=True).count()
    
    @property
    def total_storage_used(self):
        """Calculate total storage used by user's videos."""
        from django.db.models import Sum
        result = self.videos.filter(is_active=True).aggregate(
            total=Sum('file_size')
        )
        return result['total'] or 0
    
    def can_upload_video(self, file_size):
        """Check if user can upload a video based on plan limits."""
        if not self.plan:
            return False, "No active plan"
        
        from django.conf import settings
        plan_name = self.plan.name.upper()
        constraints = settings.VIDEO_CONSTRAINTS.get(plan_name, {})
        
        # Check video count limit
        max_videos = constraints.get('max_videos')
        if max_videos and self.total_videos >= max_videos:
            return False, f"Maximum {max_videos} videos allowed for {plan_name} plan"
        
        # Check storage limit
        total_storage = constraints.get('total_storage', 0)
        if self.total_storage_used + file_size > total_storage:
            return False, "Storage quota exceeded"
        
        return True, "OK"


# ============================================================================
# Staff/Client Models
# ============================================================================

class StaffProfile(models.Model):
    """Extended profile for staff users."""
    
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='staff_profile',
        limit_choices_to={'user_type': 'STAFF'}
    )
    
    # Plan-based limits
    max_clients = models.IntegerField(default=2, help_text="Maximum number of client devices allowed")
    max_storage_gb = models.IntegerField(default=5, help_text="Maximum storage in GB")
    can_use_cloud = models.BooleanField(default=False, help_text="Can upload to cloud storage")
    
    # Current usage
    active_clients_count = models.IntegerField(default=0, help_text="Number of active client devices")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'staff_profiles'
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'
    
    def __str__(self):
        return f"Staff: {self.user.email}"
    
    def can_generate_code(self):
        """Check if staff can generate more codes."""
        active_codes = AccessCode.objects.filter(
            staff=self.user,
            is_active=True
        ).count()
        return active_codes < self.max_clients
    
    def get_available_slots(self):
        """Get number of available client slots."""
        active_codes = AccessCode.objects.filter(
            staff=self.user,
            is_active=True
        ).count()
        return self.max_clients - active_codes
    
    @property
    def storage_used_gb(self):
        """Calculate storage used by staff's videos in GB."""
        from apps.videos.models import Video
        from django.db.models import Sum
        
        result = Video.objects.filter(
            owner=self.user,
            is_active=True
        ).aggregate(total=Sum('file_size'))
        
        bytes_used = result['total'] or 0
        return round(bytes_used / (1024 * 1024 * 1024), 2)
    
    @property
    def storage_available_gb(self):
        """Get available storage in GB."""
        return max(0, self.max_storage_gb - self.storage_used_gb)


class AccessCode(models.Model):
    """Access codes generated by staff for client authentication."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=12, unique=True, db_index=True, help_text="8-character alphanumeric code")
    
    # Relationships
    staff = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='generated_codes',
        limit_choices_to={'user_type': 'STAFF'}
    )
    client = models.OneToOneField(
        'ClientAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='access_code'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False, help_text="Has been activated by a client")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'access_codes'
        verbose_name = 'Access Code'
        verbose_name_plural = 'Access Codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['staff', '-created_at']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.staff.email}"
    
    @staticmethod
    def generate_unique_code():
        """Generate a unique 8-character alphanumeric code."""
        import random
        import string
        
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not AccessCode.objects.filter(code=code).exists():
                return code
    
    def activate(self, client_account):
        """Activate this code for a client account."""
        if self.is_used:
            return False, "Code already used"
        
        if not self.is_active:
            return False, "Code is inactive"
        
        self.client = client_account
        self.is_used = True
        self.activated_at = timezone.now()
        self.save()
        
        return True, "Code activated successfully"
    
    def deactivate(self):
        """Deactivate this code."""
        self.is_active = False
        self.save()
        
        # Also deactivate the client if linked
        if self.client:
            self.client.is_active = False
            self.client.save()


class ClientAccount(models.Model):
    """Client device account linked to a staff member."""
    
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='client_account',
        limit_choices_to={'user_type': 'CLIENT'}
    )
    
    # Hierarchy
    staff = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='clients',
        limit_choices_to={'user_type': 'STAFF'}
    )
    
    # Device info
    device_name = models.CharField(
        max_length=100,
        help_text="Friendly name for the device (e.g., 'Coffee Shop Main TV')"
    )
    device_identifier = models.CharField(
        max_length=255,
        blank=True,
        help_text="Hardware identifier or IP address"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False, help_text="Currently connected/playing")
    last_seen = models.DateTimeField(null=True, blank=True)
    
    # Playback state (for future real-time control)
    current_video_id = models.UUIDField(null=True, blank=True, help_text="Currently playing video")
    playback_position = models.IntegerField(default=0, help_text="Current playback position in seconds")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'client_accounts'
        verbose_name = 'Client Account'
        verbose_name_plural = 'Client Accounts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['staff', '-created_at']),
            models.Index(fields=['is_online']),
        ]
    
    def __str__(self):
        return f"{self.device_name} (Staff: {self.staff.email})"
    
    def update_online_status(self, is_online=True):
        """Update online status and last seen timestamp."""
        self.is_online = is_online
        if is_online:
            self.last_seen = timezone.now()
        self.save(update_fields=['is_online', 'last_seen', 'updated_at'])
    
    def get_assigned_videos(self):
        """Get all videos assigned to this client."""
        from apps.videos.models import StaffVideoAssignment
        
        # Get videos specifically assigned to this client
        specific_assignments = StaffVideoAssignment.objects.filter(
            assigned_to=self,
            video__is_active=True
        ).select_related('video')
        
        # Get staff-global videos
        global_assignments = StaffVideoAssignment.objects.filter(
            staff=self.staff,
            is_global_for_staff=True,
            assigned_to__isnull=True,
            video__is_active=True
        ).select_related('video')
        
        # Combine and order by play_order
        all_assignments = list(specific_assignments) + list(global_assignments)
        all_assignments.sort(key=lambda x: x.play_order)
        
        return [assignment.video for assignment in all_assignments]
