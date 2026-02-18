"""
Views for handling OTP verification.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.views.decorators.http import require_http_methods
from apps.accounts.models import User
from apps.plans.models import Plan
from apps.accounts.utils import verify_twilio_otp

@require_http_methods(["GET", "POST"])
def verify_signup_otp_view(request):
    """
    Verify OTP for user registration.
    """
    # Check if session has signup data
    signup_data = request.session.get('signup_data')
    if not signup_data:
        messages.error(request, 'Session expired. Please sign up again.')
        return redirect('signup')
        
    mobile_number = signup_data.get('mobile_number')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp', '').strip()
        
        if not otp_code:
            messages.error(request, 'Please enter the OTP.')
            return render(request, 'auth/verify_otp.html', {'mobile_number': mobile_number})
            
        # Verify OTP
        success, message = verify_twilio_otp(mobile_number, otp_code)
        
        if success:
            try:
                # Create the user from session data
                email = signup_data['email']
                username = signup_data['username']
                password = signup_data['password']
                
                # Double check uniqueness (race condition)
                if User.objects.filter(mobile_number=mobile_number).exists():
                     messages.error(request, 'Account already exists. Please login.')
                     return redirect('login')
                
                # Get the Free plan (default)
                free_plan = Plan.objects.filter(name__iexact='Free').first()
                if not free_plan:
                    # Fallback if plan doesn't exist yet
                     free_plan = Plan.objects.create(name='Free', price=0)

                # Create the user
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    username=username,
                    plan=free_plan,
                    role='USER',
                    mobile_number=mobile_number
                )
                
                # Cleanup session
                del request.session['signup_data']
                
                # Redirect to login with success message
                messages.success(request, f'Account created successfully! Please login with your username or mobile number.')
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
                return render(request, 'auth/verify_otp.html', {'mobile_number': mobile_number})
        else:
            messages.error(request, f'Verification failed: {message}')
            return render(request, 'auth/verify_otp.html', {'mobile_number': mobile_number})
            
    return render(request, 'auth/verify_otp.html', {'mobile_number': mobile_number})
