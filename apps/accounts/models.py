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
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
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
