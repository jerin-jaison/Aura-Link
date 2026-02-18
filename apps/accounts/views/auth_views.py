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
    User login with access code support for client devices.
    """
    if request.user.is_authenticated:
        # Route based on user type
        if request.user.is_admin:
            return redirect('admin_dashboard')
        elif request.user.user_type == 'CLIENT':
            return redirect('client_player')
        elif request.user.user_type == 'STAFF':
            return redirect('staff_dashboard')
        return redirect('choose_user_type')  # Regular users choose their path
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        access_code = request.POST.get('access_code', '').strip().upper()
        
        if not username or not password:
            messages.error(request, 'Please enter both username/mobile and password.')
            return render(request, 'auth/login.html')
        
        # Try to authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is blocked
            if not user.is_active:
                messages.error(request, 'Your account has been blocked. Please contact admin for more info.')
                return render(request, 'auth/login.html')
            
            # Handle access code (client device login)
            if access_code:
                from apps.accounts.models import AccessCode, ClientAccount
                
                try:
                    code_obj = AccessCode.objects.get(code=access_code, is_active=True)
                    
                    # SECURITY: Staff members cannot use access codes as clients
                    if user.user_type == 'STAFF':
                        messages.error(
                            request,
                            'Staff members cannot use access codes. Please login with your staff credentials.'
                        )
                        return render(request, 'auth/login.html')
                    
                    # Check if code is already used
                    if code_obj.is_used:
                        messages.error(request, 'This access code has already been used.')
                        return render(request, 'auth/login.html')
                    
                    # Set user type to CLIENT
                    user.user_type = 'CLIENT'
                    user.save()
                    
                    # Check if client already has an account
                    existing_client = ClientAccount.objects.filter(user=user).first()
                    
                    if existing_client:
                        # Client already linked to a staff member
                        if existing_client.access_code != code_obj:
                            # Trying to use a different access code - NOT ALLOWED
                            messages.error(
                                request, 
                                f'This device is already registered to {existing_client.staff.email}. '
                                f'Contact your administrator to unlink this device first.'
                            )
                            return render(request, 'auth/login.html')
                        else:
                            # Using same access code - just reactivate
                            existing_client.is_active = True
                            existing_client.save()
                            client_account = existing_client
                    else:
                        # Create new client account
                        client_account = ClientAccount.objects.create(
                            user=user,
                            staff=code_obj.staff,
                            access_code=code_obj,
                            device_name=f"{user.username}'s Device",
                        )
                    
                    # Activate the code (if not already activated)
                    if not code_obj.is_used:
                        success, message = code_obj.activate(client_account)
                        if not success:
                            messages.error(request, message)
                            return render(request, 'auth/login.html')
                    
                    # Login and redirect to client player
                    login(request, user)
                    messages.success(request, f'Welcome! Connected to {code_obj.staff.email}\'s content.')
                    return redirect('client_player')
                    
                except AccessCode.DoesNotExist:
                    messages.error(request, 'Invalid access code.')
                    return render(request, 'auth/login.html')
            
            # Normal login without access code
            login(request, user)
            messages.success(request, f'Login successful! Welcome back, {user.username}.')
            
            # Route based on user type
            if user.is_admin:
                return redirect('admin_dashboard')
            elif user.user_type == 'CLIENT':
                return redirect('client_player')
            elif user.user_type == 'STAFF':
                return redirect('staff_dashboard')
            else:
                # Regular user - ask what they want to be
                return redirect('choose_user_type')
        else:
            # Authentication failed
            messages.error(request, 'Invalid username/mobile number or password.')
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


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
@require_http_methods(["GET"])
def choose_user_type_view(request):
    """
    Allow users to choose if they want to be regular users or staff members.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    # If already chosen, redirect to appropriate dashboard
    if request.user.user_type == 'STAFF':
        return redirect('staff_dashboard')
    elif request.user.user_type == 'CLIENT':
        return redirect('client_player')
    elif request.user.is_admin:
        return redirect('admin_dashboard')
    
    return render(request, 'auth/choose_user_type.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
@require_http_methods(["POST"])
def set_user_type_view(request):
    """
    Set the user type (REGULAR or STAFF) and redirect to appropriate flow.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_type = request.POST.get('user_type')
    
    if user_type == 'STAFF':
        # Set user type to STAFF
        request.user.user_type = 'STAFF'
        request.user.save()
        
        # Create staff profile with default free plan limits
        from apps.accounts.models import StaffProfile
        StaffProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'max_clients': 2,
                'max_storage_gb': 5,
                'can_use_cloud': False
            }
        )
        
        messages.success(request, 'Welcome to Staff mode! Please choose a plan to get started.')
        return redirect('staff_choose_plan')  # Will create this view next
        
    elif user_type == 'REGULAR':
        # Set user type to REGULAR
        request.user.user_type = 'REGULAR'
        request.user.save()
        
        messages.success(request, 'Welcome! You can now start uploading your videos.')
        return redirect('user_dashboard')
    
    else:
        messages.error(request, 'Invalid user type selection.')
        return redirect('choose_user_type')
