"""
Staff and Client dashboard URLs.
"""

from django.urls import path
from apps.accounts.views.staff_views import (
    staff_dashboard_view,
    staff_choose_plan_view,
    staff_codes_view,
    generate_code_view,
    deactivate_code_view,
    staff_clients_view,
    edit_client_view,
    toggle_client_view,
)
from apps.accounts.views.client_views import client_player_view
from apps.accounts.views.staff_video_views import (
    staff_videos_view,
    staff_upload_video_view,
    staff_edit_video_view,
    staff_delete_video_view,
    staff_assign_video_view,
)
from apps.accounts.views.staff_views import (
    staff_settings_view, 
    staff_plans_view,
    switch_account_type_view,
)

urlpatterns = [
    # Staff URLs
    path('staff/', staff_dashboard_view, name='staff_dashboard'),
    path('staff/choose-plan/', staff_choose_plan_view, name='staff_choose_plan'),
    
    # Access Codes
    path('staff/codes/', staff_codes_view, name='staff_codes'),
    path('staff/codes/generate/', generate_code_view, name='generate_code'),
    path('staff/codes/<uuid:code_id>/deactivate/', deactivate_code_view, name='deactivate_code'),
    
    # Client Management
    path('staff/clients/', staff_clients_view, name='staff_clients'),
    path('staff/clients/<int:client_id>/edit/', edit_client_view, name='edit_client'),
    path('staff/clients/<int:client_id>/toggle/', toggle_client_view, name='toggle_client'),
    
    # Video Management
    path('staff/videos/', staff_videos_view, name='staff_videos'),
    path('staff/videos/upload/', staff_upload_video_view, name='staff_upload_video'),
    path('staff/videos/<uuid:video_id>/edit/', staff_edit_video_view, name='staff_edit_video'),
    path('staff/videos/<uuid:video_id>/delete/', staff_delete_video_view, name='staff_delete_video'),
    path('staff/videos/<uuid:video_id>/assign/', staff_assign_video_view, name='staff_assign_video'),
    
    # Settings & Plans
    path('staff/settings/', staff_settings_view, name='staff_settings'),
    path('staff/plans/', staff_plans_view, name='staff_plans'),
    
    # Account Switching
    path('switch-account-type/', switch_account_type_view, name='switch_account_type'),
    
    # Client URLs
    path('client/player/', client_player_view, name='client_player'),
]
