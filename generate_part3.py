"""
Final file generator for Audit, Tasks (Celery), Dashboard apps and critical templates.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Part 3: Audit, Tasks, Dashboard, Templates
FILES_PART_3 = {
    # Audit App
    'apps/audit/__init__.py': '',
    'apps/audit/apps.py': '''from django.apps import AppConfig

class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit'
''',

    'apps/audit/models.py': '''"""
Audit logging for admin actions.
"""

from django.db import models
from django.conf import settings


class AdminActionLog(models.Model):
    """Log all administrative actions."""
    
    ACTION_CHOICES = (
        ('USER_CREATED', 'User Created'),
        ('USER_DELETED', 'User Deleted'),
        ('PLAN_CHANGED', 'Plan Changed'),
        ('VIDEO_DISABLED', 'Video Disabled'),
        ('VIDEO_DELETED', 'Video Deleted'),
        ('FEATURE_TOGGLED', 'Feature Toggled'),
    )
    
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_model = models.CharField(max_length=50)
    target_id = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_action_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action_type']),
        ]
    
    def __str__(self):
        return f"{self.action_type} by {self.admin.email if self.admin else 'Unknown'}"
''',

    'apps/audit/decorators.py': '''"""
Decorator for logging admin actions.
"""

from functools import wraps
from .models import AdminActionLog
from apps.core.utils import get_client_ip


def log_admin_action(action_type, target_model):
    """Decorator to log admin actions."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            
            if request.user.is_authenticated and request.user.is_admin:
                # Extract target ID from kwargs or result
                target_id = kwargs.get('pk') or kwargs.get('id') or 'N/A'
                
                AdminActionLog.objects.create(
                    admin=request.user,
                    action_type=action_type,
                    target_model=target_model,
                    target_id=str(target_id),
                    description=f"{action_type} on {target_model}",
                    ip_address=get_client_ip(request)
                )
            
            return result
        return wrapper
    return decorator
''',

    'apps/audit/views.py': '''"""
Audit log views.
"""

from rest_framework import viewsets
from rest_framework.response import Response
from apps.accounts.permissions import IsAdmin
from .models import AdminActionLog


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for audit logs (admin only)."""
    
    permission_classes = [IsAdmin]
    queryset = AdminActionLog.objects.all()
    
    def list(self, request):
        """List audit logs with filtering."""
        logs = self.get_queryset()[:100]  # Latest 100
        
        data = [{
            'admin': log.admin.email if log.admin else 'System',
            'action': log.action_type,
            'target': f"{log.target_model} ({log.target_id})",
            'description': log.description,
            'ip': log.ip_address,
            'timestamp': log.timestamp
        } for log in logs]
        
        return Response(data)
''',

    'apps/audit/admin.py': '''from django.contrib import admin
from .models import AdminActionLog

@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'admin', 'target_model', 'target_id', 'timestamp']
    list_filter = ['action_type', 'timestamp']
    search_fields = ['admin__email', 'description']
    readonly_fields = ['admin', 'action_type', 'target_model', 'target_id', 'description', 'ip_address', 'timestamp']
''',

    # Billing App (Stub)
    'apps/billing/__init__.py': '',
    'apps/billing/apps.py': '''from django.apps import AppConfig

class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.billing'
''',

    'apps/billing/models.py': '''"""
Billing models (Phase 2 stub).
"""

from django.db import models
from django.conf import settings


class Invoice(models.Model):
    """Invoice model for future payment integration."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invoices'


class Transaction(models.Model):
    """Payment transaction record."""
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    gateway = models.CharField(max_length=50)  # stripe, razorpay, etc.
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transactions'
''',

    'apps/billing/admin.py': '''from django.contrib import admin
from .models import Invoice, Transaction

admin.site.register(Invoice)
admin.site.register(Transaction)
''',

    # Tasks (Celery) App
    'apps/tasks/__init__.py': '',
    'apps/tasks/apps.py': '''from django.apps import AppConfig

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'
''',

    'apps/tasks/celery.py': '''"""
Celery configuration for Aura Link.
"""

import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('auralink')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
''',

    'apps/tasks/video_tasks.py': '''"""
Celery tasks for video processing.
"""

from celery import shared_task
from apps.videos.models import Video
from apps.videos.validators import extract_video_metadata
import os


@shared_task
def process_video_metadata(video_id):
    """Extract and save video metadata."""
    
    try:
        video = Video.objects.get(id=video_id)
        
        # Get file path
        if video.storage_type == 'LOCAL':
            file_path = os.path.join('media', 'videos', video.file_path)
            
            # Extract metadata
            metadata = extract_video_metadata(file_path)
            
            # Update video
            video.duration = metadata.get('duration', 0)
            video.save()
            
            return f"Processed video {video_id}"
        
        return f"Skipped cloud video {video_id}"
    
    except Video.DoesNotExist:
        return f"Video {video_id} not found"
    except Exception as e:
        return f"Error processing {video_id}: {str(e)}"
''',

    'apps/tasks/subscription_tasks.py': '''"""
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
''',

    'apps/tasks/cleanup_tasks.py': '''"""
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
''',

    # Dashboard App
    'apps/dashboard/__init__.py': '',
    'apps/dashboard/apps.py': '''from django.apps import AppConfig

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboard'
''',

    'apps/dashboard/views.py': '''"""
Dashboard views for web interface.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.videos.models import Video
from apps.accounts.models import User
from apps.audit.models import AdminActionLog


def landing_page(request):
    """Landing page view."""
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')
    return render(request, 'landing.html')


@login_required
def user_dashboard(request):
    """User dashboard view."""
    videos = Video.objects.filter(owner=request.user, is_active=True)
    
    context = {
        'videos': videos,
        'user': request.user,
        'plan': request.user.plan,
        'total_storage': request.user.total_storage_used,
    }
    return render(request, 'dashboard/user_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Admin dashboard view."""
    if not request.user.is_admin:
        return redirect('user_dashboard')
    
    context = {
        'total_users': User.objects.count(),
        'total_videos': Video.objects.count(),
        'recent_logs': AdminActionLog.objects.all()[:10],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)
''',

    'apps/dashboard/urls.py': '''"""
Dashboard URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]
''',

    'apps/dashboard/urls_admin.py': '''"""
Admin dashboard URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
]
''',

    # Web Auth URLs
    'apps/accounts/urls/web_auth.py': '''"""
Web authentication URLs (session-based).
"""

from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
''',

    'apps/accounts/urls/__init__.py': '',

    # API Auth URLs
    'apps/accounts/urls/api_auth.py': '''"""
API authentication URLs (JWT-based).
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
''',

    #  API URLs
    'apps/accounts/urls/api.py': '''"""
User API URLs.
"""

from django.urls import path
from apps.accounts import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
''',

    # Account API Views
    'apps/accounts/views.py': '''"""
Account API views.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer, UserProfileSerializer, UserUpdateSerializer


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'User created successfully',
            'email': user.email
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint."""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileSerializer
        return UserUpdateSerializer
    
    def get_object(self):
        return self.request.user
''',

    'apps/accounts/admin.py': '''from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'plan', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'plan']
    search_fields = ['email', 'username']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username',)}),
        ('Permissions', {'fields': ('role', 'plan', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'plan'),
        }),
    )
''',
}

def create_files():
    """Create all files."""
    for file_path, content in FILES_PART_3.items():
        full_path = BASE_DIR / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() if content else '')
        
        print(f"[OK] Created: {file_path}")

if __name__ == '__main__':
    print("Generating Part 3 files...")
    create_files()
    print("\n[SUCCESS] Part 3 generated!")
