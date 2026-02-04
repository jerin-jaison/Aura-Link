"""
Dashboard URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('video/<uuid:video_id>/', views.video_player, name='video_player'),
    path('upgrade/', views.upgrade_page, name='upgrade_page'),
    path('upgrade/process/', views.process_payment, name='process_payment'),
    path('videos/manage/', views.manage_videos, name='manage_videos'),
    path('videos/<uuid:video_id>/delete/', views.delete_video, name='delete_video'),
    path('videos/<uuid:video_id>/request-deletion/', views.request_video_deletion, name='request_video_deletion'),
]