"""
Custom authentication backend to support login with email or username.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in with 
    username or mobile number.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user using username or mobile number.
        """
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by mobile number or username
            # Note: User request explicitly asked to disable email login
            # Check for standard username, mobile number, or normalized mobile (+91)
            query = Q(mobile_number=username) | Q(username__iexact=username)
            
            # If the input looks like a 10-digit number, also check for +91 version
            if username.isdigit() and len(username) == 10:
                query |= Q(mobile_number=f"+91{username}")

            user = User.objects.get(query)
            
            # Check password
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Get a user by their primary key.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
