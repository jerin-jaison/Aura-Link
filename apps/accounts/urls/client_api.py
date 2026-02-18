"""
Client-specific URL patterns for API endpoints.
"""

from django.urls import path
from apps.accounts.views.client_api_views import (
    client_playlist_api,
    client_heartbeat_api,
)

urlpatterns = [
    path('playlist/', client_playlist_api, name='client_playlist_api'),
    path('heartbeat/', client_heartbeat_api, name='client_heartbeat_api'),
]
