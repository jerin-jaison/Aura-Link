
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client
from django.urls import reverse
from apps.accounts.models import User
from apps.accounts.utils import verify_twilio_otp

def run_verification():
    print("Starting verification...")
    
    # cleanup
    User.objects.filter(mobile_number='1234567890').delete()
    User.objects.filter(mobile_number='+911234567890').delete()
    print("Cleaned up potential existing users.")

    client = Client()
    
    # 1. Signup
    print("\n1. Testing Signup...")
    signup_url = reverse('signup')
    response = client.get(signup_url)
    if response.status_code != 200:
        print(f"FAILED: Signup page load {response.status_code}")
        return

    signup_data = {
        'mobile_number': '1234567890',
        'username': 'testuser_verif',
        'email': 'test_verif@example.com',
        'password': 'Password123!',
        'password_confirm': 'Password123!'
    }
    response = client.post(signup_url, signup_data)
    
    # Expect redirect to verify otp
    if response.status_code == 302 and 'verify' in response.url:
        print("PASSED: Signup submission redirected successfully to OTP verification.")
    else:
        print(f"FAILED: Signup submission. Status: {response.status_code}, URL: {getattr(response, 'url', 'N/A')}")
        if response.context and 'form' in response.context:
             print(f"Form errors: {response.context['form'].errors}")
        return

    # 2. Verify OTP
    print("\n2. Testing OTP Verification...")
    verify_url = reverse('verify_signup_otp')
    
    # Emulate session data passing (handled by client session automatically)
    # OTP is '123456' in debug mode
    response = client.post(verify_url, {'otp': '123456'})
    
    if response.status_code == 302 and 'login' in response.url:
        print("PASSED: OTP verification redirected to Login.")
    else:
        print(f"FAILED: OTP verification. Status: {response.status_code}, URL: {getattr(response, 'url', 'N/A')}")
        return

    # Check if user exists
    user = User.objects.filter(mobile_number__in=['1234567890', '+911234567890']).first()
    if user:
        print(f"PASSED: User created in DB with mobile: {user.mobile_number}")
    else:
        print("FAILED: User not found in DB.")
        return

    # 3. Login 1 (Mobile 1234567890)
    print("\n3. Testing Login with '1234567890'...")
    login_url = reverse('login')
    client.logout() # Ensure clean session
    
    login_data = {'username': '1234567890', 'password': 'Password123!'}
    response = client.post(login_url, login_data)
    
    if response.status_code == 302 and 'home' in response.url or response.url == '/' or 'landing' in response.url or 'dashboard' in response.url:
         print(f"PASSED: Login with mobile '1234567890' successful. Redirected to {response.url}")
    else:
         print(f"FAILED: Login with mobile '1234567890'. Status: {response.status_code}, URL: {getattr(response, 'url', 'N/A')}")
         # Check if it failed because of form error
         if hasattr(response, 'context_data') and 'form' in response.context_data:
              print(f"Form errors: {response.context_data['form'].errors}")
         # Attempt to verify via check_authorization
         if '_auth_user_id' in client.session:
              print("BUT Session has user_id, so technically logged in?")


    # 4. Login 2 (Mobile +911234567890)
    print("\n4. Testing Login with '+911234567890'...")
    client.logout()
    login_data = {'username': '+911234567890', 'password': 'Password123!'}
    response = client.post(login_url, login_data)
    
    if response.status_code == 302:
         print(f"PASSED: Login with international format '+911234567890' successful. Redirected to {response.url}")
    else:
         # It depends on if the backend normalizes the input or supports searching by this format
         # If the user was saved as +91... then yes. If saved as 123... and input is +91... it depends on backend logic.
         print(f"Note: Login with '+911234567890' returned {response.status_code}. DB stored: {user.mobile_number}")
         if user.mobile_number == '1234567890':
             print("Backend might not be stripping +91 from input or normalizing automatically.")

    # 5. Login 3 (Username)
    print("\n5. Testing Login with Username 'testuser_verif'...")
    client.logout()
    login_data = {'username': 'testuser_verif', 'password': 'Password123!'}
    response = client.post(login_url, login_data)
    
    if response.status_code == 302:
         print(f"PASSED: Login with username successful. Redirected to {response.url}")
    else:
         print(f"FAILED: Login with username. Status: {response.status_code}")

if __name__ == '__main__':
    run_verification()
