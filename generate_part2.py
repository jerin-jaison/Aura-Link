"""
Extended file generator for remaining apps.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Part 2: Videos, Subscriptions, Audit, Tasks apps
FILES_PART_2 = {
    # Videos App
    'apps/videos/__init__.py': '',
    'apps/videos/apps.py': '''from django.apps import AppConfig

class VideosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.videos'
''',
    
    'apps/videos/models.py': '''"""
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
''',

    'apps/videos/validators.py': '''"""
Video file validators.
"""

from django.conf import settings
from apps.core.exceptions import FileValidationError, PlanLimitExceeded
import ffmpeg


def validate_video_upload(user, file, format):
    """Validate video upload against plan limits."""
    
    if not user.plan:
        raise PlanLimitExceeded("No active plan")
    
    plan_name = user.plan.name.upper()
    constraints = settings.VIDEO_CONSTRAINTS.get(plan_name, {})
    
    # Check file size
    max_size = constraints.get('max_file_size', 0)
    if file.size > max_size:
        raise FileValidationError(
            f"File size {file.size // (1024*1024)}MB exceeds limit of {max_size // (1024*1024)}MB"
        )
    
    # Check format
    allowed_formats = constraints.get('allowed_formats', [])
    if format.lower() not in allowed_formats:
        raise FileValidationError(
            f"Format {format} not allowed. Allowed: {', '.join(allowed_formats)}"
        )
    
    # Check video count
    can_upload, message = user.can_upload_video(file.size)
    if not can_upload:
        raise PlanLimitExceeded(message)
    
    return True


def extract_video_metadata(file_path):
    """Extract video metadata using FFmpeg."""
    
    try:
        probe = ffmpeg.probe(file_path)
        video_stream = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
            None
        )
        
        if video_stream:
            duration = float(probe['format']['duration'])
            return {
                'duration': int(duration),
                'width': video_stream.get('width'),
                'height': video_stream.get('height'),
                'codec': video_stream.get('codec_name'),
            }
    except Exception as e:
        # Fallback if FFmpeg fails
        return {'duration': 0}
    
    return {'duration': 0}
''',

    'apps/videos/storage.py': '''"""
Storage abstraction for local and cloud uploads.
"""

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class VideoStorage:
    """Abstraction layer for video storage."""
    
    @staticmethod
    def get_storage(storage_type='local'):
        """Get storage backend based on type."""
        
        if storage_type == 's3' or settings.STORAGE_TYPE == 's3':
            return S3Boto3Storage()
        else:
            return FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'videos'))
    
    @staticmethod
    def save_video(file, filename, storage_type='local'):
        """Save video to storage."""
        
        storage = VideoStorage.get_storage(storage_type)
        path = storage.save(filename, file)
        
        if storage_type == 's3':
            return storage.url(path)
        else:
            return path
    
    @staticmethod
    def delete_video(file_path, storage_type='local'):
        """Delete video from storage."""
        
        storage = VideoStorage.get_storage(storage_type)
        try:
            storage.delete(file_path)
            return True
        except Exception:
            return False
''',

    'apps/videos/serializers.py': '''"""
Video serializers.
"""

from rest_framework import serializers
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for Video model."""
    
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    file_size_mb = serializers.FloatField(read_only=True)
    duration_minutes = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Video
        fields = ['id', 'title', 'storage_type', 'file_path', 'cloud_url',
                  'file_size', 'file_size_mb', 'duration', 'duration_minutes',
                  'format', 'thumbnail_url', 'is_active', 'owner_email', 'created_at']
        read_only_fields = ['id', 'file_path', 'cloud_url', 'thumbnail_url',
                            'file_size', 'duration', 'created_at', 'is_active']


class VideoUploadSerializer(serializers.Serializer):
    """Serializer for video upload."""
    
    title = serializers.CharField(max_length=255)
    video_file = serializers.FileField()
    storage_type = serializers.ChoiceField(choices=['LOCAL', 'CLOUD'], default='LOCAL')
''',

    'apps/videos/views.py': '''"""
Video API views.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from .models import Video
from .serializers import VideoSerializer, VideoUploadSerializer
from .validators import validate_video_upload, extract_video_metadata
from .storage import VideoStorage
from apps.accounts.permissions import IsActiveUser, CanAccessVideo, CanUploadVideo
from apps.tasks.video_tasks import process_video_metadata

import os
import uuid


class VideoViewSet(viewsets.ModelViewSet):
    """ViewSet for video management."""
    
    serializer_class = VideoSerializer
    permission_classes = [IsActiveUser, CanAccessVideo]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Return videos based on user role."""
        if self.request.user.is_admin:
            return Video.objects.all()
        return Video.objects.filter(owner=self.request.user, is_active=True)
    
    @method_decorator(ratelimit(key='user', rate='100/h', method='POST'))
    @action(detail=False, methods=['post'], permission_classes=[CanUploadVideo])
    def upload(self, request):
        """Upload a new video."""
        
        serializer = VideoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        video_file = serializer.validated_data['video_file']
        title = serializer.validated_data['title']
        storage_type = serializer.validated_data['storage_type']
        
        # Detect format
        file_ext = os.path.splitext(video_file.name)[1][1:].lower()
        
        try:
            # Validate upload
            validate_video_upload(request.user, video_file, file_ext)
            
            # Check cloud upload permission
            if storage_type == 'CLOUD' and not request.user.plan.cloud_upload_allowed:
                return Response({
                    'error': 'Cloud upload not allowed for your plan'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Generate unique filename
            filename = f"{uuid.uuid4()}.{file_ext}"
            
            # Save file
            if storage_type == 'CLOUD':
                file_url = VideoStorage.save_video(video_file, filename, 's3')
                cloud_url = file_url
                file_path = ''
            else:
                file_path = VideoStorage.save_video(video_file, filename, 'local')
                cloud_url = ''
            
            # Create video record
            video = Video.objects.create(
                owner=request.user,
                title=title,
                storage_type=storage_type,
                file_path=file_path,
                cloud_url=cloud_url,
                file_size=video_file.size,
                format=file_ext
            )
            
            # Trigger background task for metadata extraction
            process_video_metadata.delay(str(video.id))
            
            return Response(
                VideoSerializer(video).data,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def playlist(self, request):
        """Get user's playlist."""
        videos = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(videos, many=True)
        
        return Response({
            'videos': serializer.data,
            'loop_enabled': request.user.plan.playlist_loop_allowed if request.user.plan else False
        })
''',

    'apps/videos/urls.py': '''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet

router = DefaultRouter()
router.register(r'', VideoViewSet, basename='video')

urlpatterns = router.urls
''',

    'apps/videos/admin.py': '''from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'storage_type', 'file_size_mb', 'duration_minutes', 'is_active', 'created_at']
    list_filter = ['storage_type', 'is_active', 'format']
    search_fields = ['title', 'owner__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
''',

    # Subscriptions App
    'apps/subscriptions/__init__.py': '',
    'apps/subscriptions/apps.py': '''from django.apps import AppConfig

class SubscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.subscriptions'
''',

    'apps/subscriptions/models.py': '''"""
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
''',

    'apps/subscriptions/views.py': '''"""
Subscription API views.
"""

from rest_framework import viewsets
from rest_framework.response import Response
from .models import Subscription


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for subscription details."""
    
    def list(self, request):
        """Get current user's subscription."""
        try:
            subscription = Subscription.objects.get(user=request.user)
            return Response({
                'plan': subscription.plan.name if subscription.plan else None,
                'status': subscription.status,
                'end_date': subscription.end_date,
                'days_until_expiry': subscription.days_until_expiry(),
                'in_grace_period': subscription.is_in_grace_period()
            })
        except Subscription.DoesNotExist:
            return Response({'plan': request.user.plan.name if request.user.plan else 'Free'})
''',

    'apps/subscriptions/urls.py': '''from django.urls import path
from .views import SubscriptionViewSet

urlpatterns = [
    path('', SubscriptionViewSet.as_view({'get': 'list'}), name='subscription-detail'),
]
''',

    'apps/subscriptions/admin.py': '''from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'days_until_expiry']
    list_filter = ['status', 'plan']
    search_fields = ['user__email']
''',
}

def create_files():
    """Create all files."""
    for file_path, content in FILES_PART_2.items():
        full_path = BASE_DIR / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() if content else '')
        
        print(f"[OK] Created: {file_path}")

if __name__ == '__main__':
    print("Generating Part 2 files...")
    create_files()
    print("\n[SUCCESS] Part 2 generated!")
