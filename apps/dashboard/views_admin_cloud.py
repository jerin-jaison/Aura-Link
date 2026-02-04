"""
Admin cloud video management views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from apps.accounts.models import User
from apps.videos.models import Video
from apps.audit.models import AdminActionLog
from django.db import transaction


@never_cache
@login_required
def admin_manage_user_videos(request, user_id):
    """Manage a specific user's cloud videos."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
    
    target_user = get_object_or_404(User, id=user_id)
    
    # Get only cloud videos for this user
    cloud_videos = Video.objects.filter(
        owner=target_user,
        storage_type='CLOUD'
    ).order_by('-created_at')
    
    # Calculate stats
    total_storage = sum(video.file_size for video in cloud_videos)
    active_count = cloud_videos.filter(is_active=True).count()
    
    context = {
        'target_user': target_user,
        'cloud_videos': cloud_videos,
        'total_storage': total_storage,
        'active_count': active_count,
        'page_title': f'Manage {target_user.email} Videos'
    }
    return render(request, 'dashboard/admin/manage_user_videos.html', context)


@never_cache
@login_required
def admin_toggle_user_video(request, user_id, video_id):
    """Toggle active status of a user's video."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
    
    if request.method != 'POST':
        return redirect('admin_manage_user_videos', user_id=user_id)
    
    target_user = get_object_or_404(User, id=user_id)
    video = get_object_or_404(Video, id=video_id, owner=target_user)
    
    # Toggle status
    video.is_active = not video.is_active
    video.save()
    
    # Log action
    action_type = "VIDEO_ACTIVATED" if video.is_active else "VIDEO_ARCHIVED"
    AdminActionLog.objects.create(
        admin=request.user,
        action_type=action_type,
        target_model="Video",
        target_id=str(video.id),
        description=f"{'Activated' if video.is_active else 'Archived'} video '{video.title}' for user {target_user.email}"
    )
    
    status = "activated" if video.is_active else "archived"
    messages.success(request, f'Video "{video.title}" has been {status}.')
    
    return redirect('admin_manage_user_videos', user_id=user_id)


@never_cache
@login_required
def admin_delete_user_video(request, user_id, video_id):
    """Permanently delete a user's cloud video."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
    
    if request.method != 'POST':
        return redirect('admin_manage_user_videos', user_id=user_id)
    
    target_user = get_object_or_404(User, id=user_id)
    video = get_object_or_404(Video, id=video_id, owner=target_user, storage_type='CLOUD')
    
    video_title = video.title
    
    try:
        with transaction.atomic():
            # Delete from cloud storage if needed
            if video.cloud_url:
                # Here you would add cloud storage deletion logic
                # For now, we'll just soft delete
                pass
            
            # Permanently delete the video record
            video.delete()
            
            # Log action
            AdminActionLog.objects.create(
                admin=request.user,
                action_type="VIDEO_DELETED",
                target_model="Video",
                target_id=str(video_id),
                description=f"Deleted cloud video '{video_title}' for user {target_user.email}"
            )
            
            messages.success(request, f'Video "{video_title}" has been permanently deleted.')
            
    except Exception as e:
        messages.error(request, f'Error deleting video: {str(e)}')
    
    return redirect('admin_manage_user_videos', user_id=user_id)
