"""
URL configuration for Aura Link project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import health_check

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Web Authentication (Session-based)
    path('auth/web/', include('apps.accounts.urls.web_auth')),
    
    # Staff & Client Dashboards
    path('', include('apps.accounts.urls.dashboards')),
    
    # API v1
    path('api/v1/', include([
        # JWT Authentication for mobile/TV
        path('auth/', include('apps.accounts.urls.api_auth')),
        
        # API endpoints
        path('users/', include('apps.accounts.urls.api')),
        path('plans/', include('apps.plans.urls')),
        path('videos/', include('apps.videos.urls')),
        path('subscriptions/', include('apps.subscriptions.urls')),
    ])),
    
    # Client API (for TV/Kiosk devices)
    path('api/client/', include('apps.accounts.urls.client_api')),
    
    # Dashboard (Web views)
    path('', include('apps.dashboard.urls')),
    
    # Admin Portal (Custom admin interface)
    path('admin-portal/', include('apps.dashboard.urls_admin')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler403 = 'apps.core.views.custom_403'
handler404 = 'apps.core.views.custom_404'
handler500 = 'apps.core.views.custom_500'

# Admin site customization
admin.site.site_header = 'Aura Link Administration'
admin.site.site_title = 'Aura Link Admin'
admin.site.index_title = 'Video Management System'
