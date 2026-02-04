"""
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