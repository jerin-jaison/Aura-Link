"""
Client API views for video playlist and playback.
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.videos.models import Video, StaffVideoAssignment
from apps.accounts.models import ClientAccount


@login_required
@require_http_methods(["GET"])
def client_playlist_api(request):
    """
    API endpoint that returns assigned videos for the logged-in client.
    Returns video playlist with URLs, rotation settings, and metadata.
    """
    # Check if user is a client
    if request.user.user_type != 'CLIENT':
        return JsonResponse({'error': 'Access denied. Clients only.'}, status=403)
    
    try:
        client_account = ClientAccount.objects.get(user=request.user)
    except ClientAccount.DoesNotExist:
        return JsonResponse({'error': 'Client account not found.'}, status=404)
    
    # Get assigned videos for this client
    assigned_videos = client_account.get_assigned_videos()
    
    # Build playlist
    playlist = []
    for video in assigned_videos:
        playlist.append({
            'id': str(video.id),
            'title': video.title,
            'url': video.get_file_url,
            'rotation': video.rotation,  # 0, 90, 180, 270
            'duration': video.duration,
            'format': video.format,
            'file_size': video.file_size,
        })
    
    # Return response with client info
    return JsonResponse({
        'success': True,
        'client': {
            'device_name': client_account.device_name,
            'staff': client_account.staff.email,
        },
        'playlist': playlist,
        'playlist_count': len(playlist),
        'loop_mode': 'playlist',  # Can be extended to per-client settings
    })


@login_required
@require_http_methods(["POST"])
def client_heartbeat_api(request):
    """
    API endpoint for client devices to send heartbeat (update last_seen, is_online).
    Called periodically by client player to maintain online status.
    """
    if request.user.user_type != 'CLIENT':
        return JsonResponse({'error': 'Access denied.'}, status=403)
    
    try:
        client_account = ClientAccount.objects.get(user=request.user)
        client_account.update_online_status(is_online=True)
        
        return JsonResponse({
            'success': True,
            'message': 'Heartbeat received',
            'is_online': client_account.is_online,
        })
    except ClientAccount.DoesNotExist:
        return JsonResponse({'error': 'Client account not found.'}, status=404)
