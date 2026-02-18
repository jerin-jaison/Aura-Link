"""
Staff video management views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Count


@login_required
def staff_videos_view(request):
    """
    Display all videos uploaded by staff with assignment stats.
    """
    if request.user.user_type != 'STAFF':
        messages.error(request, 'Access denied.')
        return redirect('choose_user_type')
    
    from apps.videos.models import Video, StaffVideoAssignment
    from apps.accounts.models import StaffProfile
    
    staff_profile = get_object_or_404(StaffProfile, user=request.user)
    
    # Get all staff videos with assignment counts
    videos =Video.objects.filter(owner=request.user, is_active=True).annotate(
        assignment_count=Count('staff_assignments')
    ).order_by('-created_at')
    
    # Calculate stats
    videos_count = videos.count()
    assigned_count = videos.filter(assignment_count__gt=0).count()
    unassigned_count = videos_count - assigned_count
    
    # Calculate storage percentage
    if staff_profile.max_storage_gb > 0:
        storage_percent = (staff_profile.storage_used_gb / staff_profile.max_storage_gb) * 100
    else:
        storage_percent = 0
    
    context = {
        'staff_profile': staff_profile,
        'videos': videos,
        'videos_count': videos_count,
        'assigned_count': assigned_count,
        'unassigned_count': unassigned_count,
        'storage_percent': storage_percent,
    }
    
    return render(request, 'dashboard/staff/videos.html', context)


@login_required
@require_http_methods(["POST"])
def staff_upload_video_view(request):
    """
    Handle video upload for staff.
    """
    if request.user.user_type != 'STAFF':
        messages.error(request, 'Access denied.')
        return redirect('choose_user_type')
    
    from apps.videos.models import Video
    from apps.accounts.models import StaffProfile
    from apps.videos.storage import VideoStorage
    from apps.tasks.video_tasks import process_video_metadata
    from django.db.models import Sum
    
    staff_profile = get_object_or_404(StaffProfile, user=request.user)
    
    # 1. Get file and metadata
    if 'video_file' not in request.FILES:
        messages.error(request, 'No video file provided.')
        return redirect('staff_videos')
        
    video_file = request.FILES['video_file']
    title = request.POST.get('title', '').strip() or video_file.name
    rotation = int(request.POST.get('rotation', 0))
    
    # 2. Validation
    # Check format
    allowed_formats = ['mp4', 'mkv', 'webm']
    ext = video_file.name.split('.')[-1].lower() if '.' in video_file.name else ''
    if ext not in allowed_formats:
        messages.error(request, f'Invalid format. Allowed: {", ".join(allowed_formats)}')
        return redirect('staff_videos')
    
    # Check storage limit (in bytes)
    max_bytes = staff_profile.max_storage_gb * 1024 * 1024 * 1024
    used_bytes = Video.objects.filter(
        owner=request.user, 
        is_active=True
    ).aggregate(total=Sum('file_size'))['total'] or 0
    
    if used_bytes + video_file.size > max_bytes:
        messages.error(request, f'Storage limit of {staff_profile.max_storage_gb}GB exceeded.')
        return redirect('staff_videos')

    try:
        # 3. Save file
        # Determine storage type based on staff profile permissions
        storage_type = 'CLOUD' if staff_profile.can_use_cloud else 'LOCAL'
        
        # Generate safe filename
        import uuid
        file_ext = video_file.name.split('.')[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"
        
        # Save using abstraction layer
        saved_path = VideoStorage.save_video(video_file, filename, storage_type)
        
        # 4. Create DB Entry
        video = Video(
            owner=request.user,
            title=title,
            storage_type=storage_type,
            file_size=video_file.size,
            format=ext,
            rotation=rotation,
            uploaded_by_admin=False,
            is_global=False
        )
        
        if storage_type == 'CLOUD':
            video.cloud_url = saved_path
            video.file_path = filename # Store filename for reference
        else:
            video.file_path = filename
            
        video.save()
        
        # 5. Process metadata asynchronously
        process_video_metadata.delay(video.id)
        
        messages.success(request, 'Video uploaded successfully! Processing started.')
        
    except Exception as e:
        messages.error(request, f'Upload failed: {str(e)}')
    
    return redirect('staff_videos')


@login_required
@require_http_methods(["POST"])
def staff_edit_video_view(request, video_id):
    """
    Edit video settings (title, rotation).
    """
    if request.user.user_type != 'STAFF':
        messages.error(request, 'Access denied.')
        return redirect('choose_user_type')
    
    from apps.videos.models import Video
    
    video = get_object_or_404(Video, id=video_id, owner=request.user)
    
    title = request.POST.get('title', '').strip()
    rotation = int(request.POST.get('rotation', 0))
    
    if title:
        video.title = title
    
    if rotation in [0, 90, 180, 270]:
        video.rotation = rotation
    
    video.save()
    messages.success(request, f'Video "{video.title}" updated successfully.')
    
    return redirect('staff_videos')


@login_required
@require_http_methods(["POST"])
def staff_delete_video_view(request, video_id):
    """
    Delete a staff video.
    """
    if request.user.user_type != 'STAFF':
        messages.error(request, 'Access denied.')
        return redirect('choose_user_type')
    
    from apps.videos.models import Video
    
    video = get_object_or_404(Video, id=video_id, owner=request.user)
    
    video_title = video.title
    video.delete()
    
    messages.success(request, f'Video "{video_title}" deleted successfully.')
    return redirect('staff_videos')


@login_required
def staff_assign_video_view(request, video_id):
    """
    Assign video to specific clients or all clients.
    """
    if request.user.user_type != 'STAFF':
        messages.error(request, 'Access denied.')
        return redirect('choose_user_type')
    
    from apps.videos.models import Video, StaffVideoAssignment
    from apps.accounts.models import ClientAccount
    
    video = get_object_or_404(Video, id=video_id, owner=request.user)
    clients = ClientAccount.objects.filter(staff=request.user, is_active=True)
    
    # Get existing assignments
    existing_assignments = StaffVideoAssignment.objects.filter(
        video=video,
        staff=request.user
    ).values_list('assigned_to_id', flat=True)
    
    if request.method == 'POST':
        assignment_type = request.POST.get('assignment_type')
        
        if assignment_type == 'global':
            # Assign to all clients (remove specific assignments)
            StaffVideoAssignment.objects.filter(video=video, staff=request.user).delete()
            StaffVideoAssignment.objects.create(
                video=video,
                staff=request.user,
                is_global_for_staff=True,
                play_order=0
            )
            messages.success(request, f'Video assigned to ALL your clients.')
            
        elif assignment_type == 'specific':
            # Assign to specific clients
            selected_clients = request.POST.getlist('clients')
            
            # Remove old assignments
            StaffVideoAssignment.objects.filter(video=video, staff=request.user).delete()
            
            # Create new assignments
            for client_id in selected_clients:
                try:
                    client = ClientAccount.objects.get(id=client_id, staff=request.user)
                    StaffVideoAssignment.objects.create(
                        video=video,
                        staff=request.user,
                        assigned_to=client,
                        play_order=0
                    )
                except ClientAccount.DoesNotExist:
                    pass
            
            messages.success(request, f'Video assigned to {len(selected_clients)} client(s).')
        
        return redirect('staff_videos')
    
    context = {
        'video': video,
        'clients': clients,
        'existing_assignments': list(existing_assignments),
    }
    
    return render(request, 'dashboard/staff/assign_video.html', context)
