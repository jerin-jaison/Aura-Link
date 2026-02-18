from django.urls import path
from . import views
from . import views_admin
from . import views_admin_cloud

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views_admin.admin_users, name='admin_users'),
    path('users/<uuid:user_id>/toggle/', views_admin.admin_user_toggle_status, name='admin_user_toggle_status'),
    path('users/<uuid:user_id>/change-plan/', views_admin.admin_user_change_plan, name='admin_user_change_plan'),
    path('users/<uuid:user_id>/toggle-staff/', views_admin.admin_user_toggle_staff, name='admin_user_toggle_staff'),
    path('users/<uuid:user_id>/change-staff-plan/', views_admin.admin_user_change_staff_plan, name='admin_user_change_staff_plan'),
    path('users/<uuid:user_id>/videos/', views_admin_cloud.admin_manage_user_videos, name='admin_manage_user_videos'),
    path('users/<uuid:user_id>/videos/<uuid:video_id>/toggle/', views_admin_cloud.admin_toggle_user_video, name='admin_toggle_user_video'),
    path('users/<uuid:user_id>/videos/<uuid:video_id>/delete/', views_admin_cloud.admin_delete_user_video, name='admin_delete_user_video'),
    path('videos/', views_admin.admin_videos, name='admin_videos'),
    path('videos/<uuid:video_id>/toggle/', views_admin.admin_video_toggle, name='admin_video_toggle'),
    path('videos/upload/global/', views_admin.admin_upload_video_global, name='admin_upload_video_global'),
    path('users/<uuid:user_id>/upload/', views_admin.admin_upload_video_user, name='admin_upload_video_user'),
    path('deletion-requests/', views_admin.admin_deletion_requests, name='admin_deletion_requests'),
    path('deletion-requests/<uuid:request_id>/approve/', views_admin.admin_approve_deletion, name='admin_approve_deletion'),
    path('deletion-requests/<uuid:request_id>/reject/', views_admin.admin_reject_deletion, name='admin_reject_deletion'),
]