"""
Admin dashboard views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from apps.accounts.models import User
from apps.videos.models import Video
from apps.plans.models import Plan
from apps.plans.models import Plan
from apps.audit.models import AdminActionLog
from apps.videos.storage import VideoStorage
from apps.videos.validators import validate_video_upload
from apps.tasks.video_tasks import process_video_metadata
import uuid, os
from django.db import transaction, models

@never_cache
@login_required
def admin_users(request):
    """List all users."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
        
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(
            models.Q(email__icontains=query) | 
            models.Q(username__icontains=query)
        ).order_by('-created_at')
    else:
        users = User.objects.all().order_by('-created_at')
    
    context = {
        'users': users,
        'page_title': 'User Management'
    }
    return render(request, 'dashboard/admin/users.html', context)

@never_cache
@login_required
def admin_videos(request):
    """List all videos."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
        
    query = request.GET.get('q')
    if query:
        videos = Video.objects.filter(
            models.Q(title__icontains=query) | 
            models.Q(owner__email__icontains=query)
        ).order_by('-created_at')
    else:
        videos = Video.objects.all().order_by('-created_at')
    
    context = {
        'videos': videos,
        'page_title': 'Video Management'
    }
    return render(request, 'dashboard/admin/videos.html', context)

@never_cache
@login_required
def admin_video_toggle(request, video_id):
    """Toggle video status (moderation)."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
        
    video = get_object_or_404(Video, id=video_id)
    video.is_active = not video.is_active
    video.save()
    
    status = "activated" if video.is_active else "deactivated"
    messages.success(request, f'Video "{video.title}" has been {status}.')
    
    # Log action
    AdminActionLog.objects.create(
        admin=request.user,
        action_type="VIDEO_DISABLED",
        target_model="Video",
        target_id=str(video.id),
        description=f"Video status changed to: {status}"
    )
    
    return redirect('admin_videos')


@never_cache
@login_required
def admin_user_toggle_status(request, user_id):
    """Toggle user active status (Block/Unblock)."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
        
    user = get_object_or_404(User, id=user_id)
    
    # Prevent admin from blocking themselves
    if user.id == request.user.id:
        messages.error(request, "You cannot block your own account.")
        return redirect('admin_users')
        
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "blocked"
    messages.success(request, f'User "{user.email}" has been {status}.')
    
    # Log action
    AdminActionLog.objects.create(
        admin=request.user,
        action_type="FEATURE_TOGGLED",
        target_model="User",
        target_id=str(user.id),
        description=f"User status changed to: {status}"
    )
    
    return redirect('admin_users')

@never_cache
@login_required
def admin_user_change_plan(request, user_id):
    """Change user plan."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
        
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        plan_name = request.POST.get('plan_name')
        
        try:
            new_plan = Plan.objects.get(name__iexact=plan_name)
            old_plan_name = user.plan.name if user.plan else "None"
            
            user.plan = new_plan
            user.save()
            
            messages.success(request, f'User {user.email} upgraded to {new_plan.name} plan.')
            
            # Log action
            AdminActionLog.objects.create(
                admin=request.user,
                action_type="PLAN_CHANGED",
                target_model="User",
                target_id=str(user.id),
                description=f"Changed from {old_plan_name} to {new_plan.name}"
            )
            
        except Plan.DoesNotExist:
            messages.error(request, f'Plan "{plan_name}" not found.')
        except Exception as e:
            messages.error(request, f'Error updating plan: {str(e)}')
            
    return redirect('admin_users')


@never_cache
@login_required
def admin_upload_video_global(request):
    """Upload a global video visible to all users."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        video_file = request.FILES.get('video_file')
        storage_type = request.POST.get('storage_type', 'LOCAL')
        
        try:
            with transaction.atomic():
                file_ext = os.path.splitext(video_file.name)[1][1:].lower()
                validate_video_upload(request.user, video_file, file_ext)
                
                filename = f"{uuid.uuid4()}.{file_ext}"
                
                if storage_type == 'CLOUD':
                    file_url = VideoStorage.save_video(video_file, filename, 's3')
                    cloud_url = file_url
                    file_path = ''
                else:
                    file_path = VideoStorage.save_video(video_file, filename, 'local')
                    cloud_url = ''
                
                video = Video.objects.create(
                    owner=request.user,
                    title=title,
                    storage_type=storage_type,
                    file_path=file_path,
                    cloud_url=cloud_url,
                    file_size=video_file.size,
                    format=file_ext,
                    is_global=True,
                    uploaded_by_admin=True
                )
                
                process_video_metadata.delay(str(video.id))
                
                messages.success(request, 'Global video uploaded successfully.')
                
                AdminActionLog.objects.create(
                    admin=request.user,
                    action_type="GLOBAL_VIDEO_UPLOAD",
                    target_model="Video",
                    target_id=str(video.id),
                    description=f"Uploaded global video: {title}"
                )
                return redirect('admin_videos')
                
        except Exception as e:
            messages.error(request, f'Error uploading video: {str(e)}')
            
    return render(request, 'dashboard/admin/add_video_global.html')


@never_cache
@login_required
def admin_upload_video_user(request, user_id):
    """Upload a video for a specific user."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
        
    target_user = get_object_or_404(User, id=user_id)
        
    if request.method == 'POST':
        title = request.POST.get('title')
        video_file = request.FILES.get('video_file')
        storage_type = request.POST.get('storage_type', 'LOCAL')
        
        try:
            with transaction.atomic():
                file_ext = os.path.splitext(video_file.name)[1][1:].lower()
                validate_video_upload(target_user, video_file, file_ext)
                
                filename = f"{uuid.uuid4()}.{file_ext}"
                
                if storage_type == 'CLOUD':
                    file_url = VideoStorage.save_video(video_file, filename, 's3')
                    cloud_url = file_url
                    file_path = ''
                else:
                    file_path = VideoStorage.save_video(video_file, filename, 'local')
                    cloud_url = ''
                
                video = Video.objects.create(
                    owner=target_user,
                    title=title,
                    storage_type=storage_type,
                    file_path=file_path,
                    cloud_url=cloud_url,
                    file_size=video_file.size,
                    format=file_ext,
                    is_global=False,
                    uploaded_by_admin=True
                )
                
                process_video_metadata.delay(str(video.id))
                
                messages.success(request, f'Video uploaded for {target_user.email}.')
                
                AdminActionLog.objects.create(
                    admin=request.user,
                    action_type="USER_VIDEO_UPLOAD",
                    target_model="Video",
                    target_id=str(video.id),
                    description=f"Uploaded video for {target_user.email}: {title}"
                )
                return redirect('admin_users')
                
        except Exception as e:
            messages.error(request, f'Error uploading video: {str(e)}')
            
    return render(request, 'dashboard/admin/add_video_user.html', {'target_user': target_user})


@never_cache
@login_required
def admin_deletion_requests(request):
    """List all video deletion requests."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
    
    from apps.videos.deletion_requests import VideoDeletionRequest
    
    status_filter = request.GET.get('status', 'PENDING')
    
    if status_filter == 'ALL':
        requests = VideoDeletionRequest.objects.all()
    else:
        requests = VideoDeletionRequest.objects.filter(status=status_filter)
    
    context = {
        'deletion_requests': requests,
        'status_filter': status_filter,
        'page_title': 'Video Deletion Requests'
    }
    return render(request, 'dashboard/admin/deletion_requests.html', context)


@never_cache
@login_required
def admin_approve_deletion(request, request_id):
    """Approve a deletion request and delete the video."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
    
    from apps.videos.deletion_requests import VideoDeletionRequest
    from django.utils import timezone
    
    deletion_request = get_object_or_404(VideoDeletionRequest, id=request_id)
    
    if deletion_request.status != 'PENDING':
        messages.warning(request, 'This request has already been processed.')
        return redirect('admin_deletion_requests')
    
    try:
        with transaction.atomic():
            video = deletion_request.video
            video_title = video.title
            requester_email = deletion_request.requested_by.email
            
            # Update request status
            deletion_request.status = 'APPROVED'
            deletion_request.resolved_by = request.user
            deletion_request.resolved_at = timezone.now()
            deletion_request.save()
            
            # Delete the video (soft delete)
            video.is_active = False
            video.save()
            
            # Log action
            AdminActionLog.objects.create(
                admin=request.user,
                action_type="DELETION_APPROVED",
                target_model="Video",
                target_id=str(video.id),
                description=f"Approved deletion of '{video_title}' requested by {requester_email}"
            )
            
            messages.success(request, f'Deletion request approved. Video "{video_title}" has been deleted.')
            
    except Exception as e:
        messages.error(request, f'Error approving deletion: {str(e)}')
    
    return redirect('admin_deletion_requests')


@never_cache
@login_required
def admin_reject_deletion(request, request_id):
    """Reject a deletion request."""
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to access the admin panel.")
        return redirect('user_dashboard')
    
    from apps.videos.deletion_requests import VideoDeletionRequest
    from django.utils import timezone
    
    deletion_request = get_object_or_404(VideoDeletionRequest, id=request_id)
    
    if deletion_request.status != 'PENDING':
        messages.warning(request, 'This request has already been processed.')
        return redirect('admin_deletion_requests')
    
    if request.method == 'POST':
        admin_notes = request.POST.get('admin_notes', '')
        
        try:
            deletion_request.status = 'REJECTED'
            deletion_request.resolved_by = request.user
            deletion_request.resolved_at = timezone.now()
            deletion_request.admin_notes = admin_notes
            deletion_request.save()
            
            # Log action
            AdminActionLog.objects.create(
                admin=request.user,
                action_type="DELETION_REJECTED",
                target_model="Video",
                target_id=str(deletion_request.video.id),
                description=f"Rejected deletion of '{deletion_request.video.title}' requested by {deletion_request.requested_by.email}"
            )
            
            messages.success(request, f'Deletion request rejected.')
            
        except Exception as e:
            messages.error(request, f'Error rejecting deletion: {str(e)}')
    
    return redirect('admin_deletion_requests')

