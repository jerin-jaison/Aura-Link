"""
Client player views.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def client_player_view(request):
    """
    Client video player page showing assigned videos.
    """
    # Ensure user is a client
    if request.user.user_type != 'CLIENT':
        messages.error(request, 'Access denied. This page is for client devices only.')
        return redirect('choose_user_type')
    
    from apps.accounts.models import ClientAccount
    
    try:
        client = ClientAccount.objects.get(user=request.user)
        
        # Get assigned videos (excludes admin global videos)
        videos = client.get_assigned_videos()
        
        # Update online status
        client.update_online_status(is_online=True)
        
        context = {
            'client': client,
            'videos': videos,
        }
        
        return render(request, 'dashboard/client/player.html', context)
        
    except ClientAccount.DoesNotExist:
        messages.error(request, 'Client account not found. Please use an access code to login.')
        return redirect('logout')
