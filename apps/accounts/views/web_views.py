"""
Web authentication views for session-based login.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from apps.accounts.models import User
from apps.plans.models import Plan


@require_http_methods(["GET", "POST"])
def signup_view(request):
    """
    Handle user registration with username and email.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation
        if not email or not username or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'auth/signup.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/signup.html')
        
        # Check if email already exists
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'auth/signup.html')
        
        # Check if username already exists
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'auth/signup.html')
        
        try:
            # Get the Free plan (default)
            free_plan = Plan.objects.filter(name__iexact='Free').first()
            
            # Create the user
            user = User.objects.create_user(
                email=email,
                password=password,
                username=username,
                plan=free_plan,
                role='USER'
            )
            
            # Specify the backend to avoid "multiple backends configured" error
            user.backend = 'apps.accounts.backends.EmailOrUsernameBackend'
            
            # Log the user in
            login(request, user)
            messages.success(request, f'Welcome to Aura Link, {username}!')
            return redirect('user_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'auth/signup.html')
    
    return render(request, 'auth/signup.html')
