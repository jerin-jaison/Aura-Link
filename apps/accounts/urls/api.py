"""
User API URLs.
"""

from django.urls import path
from apps.accounts import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]