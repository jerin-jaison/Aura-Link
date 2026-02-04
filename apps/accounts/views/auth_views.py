"""
Custom authentication views with enhanced error messages.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache, cache_control
from apps.accounts.models import User


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
@require_http_methods(["GET", "POST"])
def user_login_view(request):
    """
    User login with enhanced error messages.
    """
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please enter both email/username and password.')
            return render(request, 'auth/login.html')
        
        # Try to authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is blocked
            if not user.is_active:
                messages.error(request, 'Your account has been blocked. Please contact admin for more info.')
                return render(request, 'auth/login.html')
            
            # Login successful
            login(request, user)
            messages.success(request, f'Login successful! Welcome back, {user.username}.')
            
            # Redirect based on role
            if user.is_admin:
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            # Authentication failed
            messages.error(request, 'Invalid email/username or password.')
            return render(request, 'auth/login.html')
    
    return render(request, 'auth/login.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
@require_http_methods(["GET", "POST"])
def admin_login_view(request):
    """
    Admin login with role verification and enhanced error messages.
    """
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin_dashboard')
        else:
            return redirect('user_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please enter both email/username and password.')
            return render(request, 'auth/admin_login.html')
        
        # Try to authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is an admin
            if not user.is_admin:
                messages.error(request, 'Access denied. This portal is for administrators only.')
                return render(request, 'auth/admin_login.html')
            
            # Check if admin is blocked
            if not user.is_active:
                messages.error(request, 'Your account has been blocked. Please contact support.')
                return render(request, 'auth/admin_login.html')
            
            # Login successful
            login(request, user)
            messages.success(request, f'Login successful! Welcome, Administrator {user.username}.')
            return redirect('admin_dashboard')
        else:
            # Authentication failed
            messages.error(request, 'Invalid credentials.')
            return render(request, 'auth/admin_login.html')
    
    return render(request, 'auth/admin_login.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def custom_logout_view(request):
    """
    Logout the user and clear session to prevent back-button access.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

