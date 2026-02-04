"""
Custom DRF permissions for Aura Link.
"""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission class to check if user is admin."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsActiveUser(permissions.BasePermission):
    """Permission class to check if user is active."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class CanAccessVideo(permissions.BasePermission):
    """Permission to check if user can access a video."""
    
    def has_object_permission(self, request, view, obj):
        # Admins can access all videos
        if request.user.is_admin:
            return True
        
        # Users can only access their own videos
        return obj.owner == request.user


class CanUploadVideo(permissions.BasePermission):
    """Permission to check if user can upload videos."""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check if user is in grace period or has expired subscription
        if hasattr(request.user, 'subscription'):
            subscription = request.user.subscription
            if subscription.status == 'EXPIRED':
                return False
        
        return True
