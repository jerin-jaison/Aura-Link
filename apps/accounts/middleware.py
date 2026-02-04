"""
Plan enforcement middleware for Aura Link.
"""

from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from apps.subscriptions.models import Subscription


class PlanEnforcementMiddleware:
    """Middleware to enforce plan limits and permissions."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip middleware for unauthenticated users and certain paths
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip for admin users
        if request.user.is_admin:
            return self.get_response(request)
        
        # Skip for auth and static endpoints
        skip_paths = ['/auth/', '/static/', '/media/', '/health/', '/admin/']
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)
        
        # Check subscription status
        try:
            subscription = Subscription.objects.get(user=request.user)
            
            # If in grace period, allow read-only access
            if subscription.status == 'IN_GRACE_PERIOD':
                if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    if '/api/' in request.path:
                        return JsonResponse({
                            'error': 'Subscription expired. Read-only access during grace period.'
                        }, status=403)
                    else:
                        return redirect('subscription_expired')
            
            # If expired, block access to most features
            elif subscription.status == 'EXPIRED':
                if '/api/' in request.path:
                    return JsonResponse({
                        'error': 'Subscription expired. Please renew to continue.'
                    }, status=403)
                else:
                    return redirect('subscription_expired')
        
        except Subscription.DoesNotExist:
            # No subscription found, user can still use Free plan
            pass
        
        response = self.get_response(request)
        return response
