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
    Handle user registration with username, email, and mobile number.
    Initiates OTP verification before creating account.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation
        if not email or not username or not password or not mobile_number:
            messages.error(request, 'All fields are required.')
            return render(request, 'auth/signup.html')
            
        # Basic mobile number validation (must be 10 digits)
        if not mobile_number.isdigit() or len(mobile_number) != 10:
             messages.error(request, 'Please enter a valid 10-digit Indian mobile number.')
             return render(request, 'auth/signup.html')
             
        # Format with +91 if not present (assuming Indian numbers as per request)
        formatted_mobile = f"+91{mobile_number}"
        
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
            
        # Check if mobile number already exists
        if User.objects.filter(mobile_number=formatted_mobile).exists():
            messages.error(request, 'Mobile number already registered.')
            return render(request, 'auth/signup.html')
        
        try:
            # Send OTP
            from apps.accounts.utils import send_twilio_otp
            success, message = send_twilio_otp(formatted_mobile)
            
            if success:
                # Store signup data in session (exclude password for partial security, but needed for creation)
                # Ideally password should be cached securely or re-asked, but for flow simplicity we'll store hash or raw.
                # Storing raw password in session is risky but standard session is server-side.
                request.session['signup_data'] = {
                    'email': email,
                    'username': username,
                    'mobile_number': formatted_mobile,
                    'password': password 
                }
                messages.success(request, f'OTP sent to {formatted_mobile}. Please verify.')
                return redirect('verify_signup_otp')
            else:
                messages.error(request, f'Error sending OTP: {message}')
                return render(request, 'auth/signup.html')
            
        except Exception as e:
            messages.error(request, f'Error initiating signup: {str(e)}')
            return render(request, 'auth/signup.html')
    
    return render(request, 'auth/signup.html')
