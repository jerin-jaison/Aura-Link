"""
Automated file generator for Aura Link project.
Run this script to generate all remaining project files.

Usage:
    python generate_project_files.py
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# File templates
FILES_TO_CREATE = {
    # Plans App
    'apps/plans/__init__.py': '',
    'apps/plans/apps.py': '''from django.apps import AppConfig

class PlansConfig(AppConfig):
    default_auto_field =  'django.db.models.BigAutoField'
    name = 'apps.plans'
''',
    
    'apps/plans/models.py': '''"""
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
    features = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'plans'
        ordering = ['price']
    
    def __str__(self):
        return self.name
''',

    'apps/plans/serializers.py': '''"""
Serializers for Plan model.
"""

from rest_framework import serializers
from .models import Plan


class PlanSerializer(serializers.ModelSerializer):
    """Serializer for Plan model."""
    
    class Meta:
        model = Plan
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
''',

    'apps/plans/views.py': '''"""
API views for plans.
"""

from rest_framework import viewsets, permissions
from .models import Plan
from .serializers import PlanSerializer


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing plans."""
    
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]
''',

    'apps/plans/urls.py': '''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanViewSet

router = DefaultRouter()
router.register(r'', PlanViewSet, basename='plan')

urlpatterns = router.urls
''',

    'apps/plans/admin.py': '''from django.contrib import admin
from .models import Plan

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'max_videos', 'cloud_upload_allowed', 'playlist_loop_allowed']
    search_fields = ['name']
''',

    'apps/plans/fixtures/initial_plans.json': '''[
    {
        "model": "plans.plan",
        "pk": 1,
        "fields": {
            "name": "Free",
            "price": "0.00",
            "max_videos": 5,
            "cloud_upload_allowed": false,
            "playlist_loop_allowed": false,
            "features": {
                "max_file_size_mb": 100,
                "max_duration_minutes": 10,
                "allowed_formats": ["mp4"],
                "total_storage_mb": 500
            }
        }
    },
    {
        "model": "plans.plan",
        "pk": 2,
        "fields": {
            "name": "Premium",
            "price": "9.99",
            "max_videos": null,
            "cloud_upload_allowed": true,
            "playlist_loop_allowed": true,
            "features": {
                "max_file_size_mb": 500,
                "max_duration_minutes": 60,
                "allowed_formats": ["mp4", "mkv", "webm"],
                "total_storage_gb": 50
            }
        }
    }
]
''',

    # Core App Files
    'apps/core/__init__.py': '',
    'apps/core/apps.py': '''from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
''',

    'apps/core/utils.py': '''"""
Shared utility functions.
"""

import magic
from django.core.files.uploadedfile import UploadedFile


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_file_type(file: UploadedFile, allowed_types: list):
    """Validate file type using magic numbers."""
    try:
        file_type = magic.from_buffer(file.read(2048), mime=True)
        file.seek(0)  # Reset file pointer
        
        # Map MIME types to extensions
        mime_map = {
            'video/mp4': 'mp4',
            'video/x-matroska': 'mkv',
            'video/webm': 'webm',
        }
        
        detected_type = mime_map.get(file_type)
        return detected_type in allowed_types
    except Exception:
        return False
''',

    'apps/core/exceptions.py': '''"""
Custom exception handling.
"""

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Custom DRF exception handler with logging."""
    
    response = drf_exception_handler(exc, context)
    
    if response is not None:
        # Log the error
        logger.error(f"API Exception: {exc}", extra={
            'view': context.get('view'),
            'request': context.get('request'),
        })
        
        # Customize error response
        response.data = {
            'error': str(exc),
            'status_code': response.status_code
        }
    
    return response


class PlanLimitExceeded(Exception):
    """Exception raised when plan limits are exceeded."""
    pass


class FileValidationError(Exception):
    """Exception for file validation errors."""
    pass
''',

    'apps/core/views.py': '''"""
Core views for health checks and error pages.
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection
from django.core.cache import cache
import redis as redis_client


def health_check(request):
    """Health check endpoint."""
    
    status = {
        'status': 'healthy',
        'database': 'unknown',
        'redis': 'unknown',
        'celery': 'unknown',
        'storage': 'unknown',
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['database'] = 'connected'
    except Exception:
        status['status'] = 'unhealthy'
        status['database'] = 'disconnected'
    
    # Check Redis
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            status['redis'] = 'connected'
    except Exception:
        status['status'] = 'unhealthy'
        status['redis'] = 'disconnected'
    
    return JsonResponse(status)


def custom_403(request, exception=None):
    """Custom 403 error page."""
    return render(request, 'errors/403.html', status=403)


def custom_404(request, exception=None):
    """Custom 404 error page."""
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    """Custom 500 error page."""
    return render(request, 'errors/500.html', status=500)
''',

    # Management command for superuser creation
    'apps/accounts/management/__init__.py': '',
    'apps/accounts/management/commands/__init__.py': '',
    'apps/accounts/management/commands/create_admin.py': '''"""
Management command to create default admin user.
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.plans.models import Plan


class Command(BaseCommand):
    help = 'Create default admin user'
    
    def handle(self, *args, **kwargs):
        email = 'jerinjaison07@gmail.com'
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Admin user {email} already exists'))
            return
        
        # Get Premium plan
        try:
            premium_plan = Plan.objects.get(name='Premium')
        except Plan.DoesNotExist:
            self.stdout.write(self.style.ERROR('Premium plan not found. Run: python manage.py loaddata initial_plans'))
            return
        
        # Create admin
        admin = User.objects.create_superuser(
            email=email,
            password='123',
            plan=premium_plan
        )
        admin.username = 'admin'
        admin.save()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {email} / 123'))
''',
}

def create_files():
    """Create all project files."""
    
    for file_path, content in FILES_TO_CREATE.items():
        full_path = BASE_DIR / file_path
        
        # Create directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() if content else '')
        
        print(f"[OK] Created: {file_path}")

if __name__ == '__main__':
    print("Generating Aura Link project files...")
    create_files()
    print("\n[SUCCESS] All files generated successfully!")
    print("\nNext steps:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. python manage.py loaddata initial_plans")
    print("4. python manage.py create_admin")
    print("5. python manage.py runserver")
