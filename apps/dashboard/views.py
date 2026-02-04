"""
Dashboard views for web interface.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.db import models
from apps.videos.models import Video
from apps.accounts.models import User
from apps.audit.models import AdminActionLog
from apps.plans.models import Plan
from apps.billing.models import Invoice, Transaction
import uuid


def landing_page(request):
    """Landing page view."""
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')
    return render(request, 'landing.html')


@never_cache
@login_required
def user_dashboard(request):
    """User dashboard view."""
    # Show user's videos AND global videos
    videos = Video.objects.filter(
        models.Q(owner=request.user) | models.Q(is_global=True),
        is_active=True
    ).distinct().order_by('-created_at')
    
    context = {
        'videos': videos,
        'user': request.user,
        'plan': request.user.plan,
        'total_storage': request.user.total_storage_used,
    }
    return render(request, 'dashboard/user_dashboard.html', context)


@never_cache
@login_required
def admin_dashboard(request):
    """Admin dashboard view."""
    if not request.user.is_admin:
        return redirect('user_dashboard')
    
    from apps.videos.deletion_requests import VideoDeletionRequest
    
    context = {
        'total_users': User.objects.count(),
        'total_videos': Video.objects.count(),
        'pending_deletions': VideoDeletionRequest.objects.filter(status='PENDING').count(),
        'recent_logs': AdminActionLog.objects.all()[:10],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@never_cache
@login_required
def video_player(request, video_id):
    """Video player view."""
    # Allow admins to view any video
    # Users can view their own videos OR global videos
    if request.user.is_admin:
        video = get_object_or_404(Video, id=video_id)
        next_video = None # Admins don't have a playlist context usually
    else:
        # User playlist context
        queryset = Video.objects.filter(
            models.Q(owner=request.user) | models.Q(is_global=True),
            is_active=True
        ).order_by('-created_at')
        
        # Get accessible video
        video = queryset.filter(id=video_id).first()
        
        if not video:
            from django.http import Http404
            raise Http404("Video not found")
            
    import json
    
    # Prepare context
    playlist_json = []
    next_video = None
    
    if request.GET.get('loop_all') == 'true':
        # Serialize accessible videos for JS playlist
        for v in queryset:
            playlist_json.append({
                'id': str(v.id),
                'title': v.title,
                'url': v.get_file_url,
                'format': v.format,
                'is_admin': v.is_global or v.owner.is_admin
            })
    else:
        # Standard Next Video Logic for UI hint (optional)
        next_video = queryset.filter(created_at__lt=video.created_at).first()

    context = {
        'video': video,
        'next_video': next_video,
        'is_loop_all': request.GET.get('loop_all') == 'true',
        'playlist_json': json.dumps(playlist_json)
    }
    return render(request, 'dashboard/video_player.html', context)


@never_cache
@login_required
def manage_videos(request):
    """Manage user videos."""
    # Show user's videos AND global videos (same as dashboard)
    videos = Video.objects.filter(
        models.Q(owner=request.user) | models.Q(is_global=True),
        is_active=True
    ).distinct().order_by('-created_at')
    
    return render(request, 'dashboard/manage_videos.html', {
        'videos': videos
    })


@never_cache
@login_required
def delete_video(request, video_id):
    """Delete a video."""
    video = get_object_or_404(Video, id=video_id)
    
    # Use the video model's method to check deletion permission
    if not video.can_be_deleted_by_user(request.user):
        if video.uploaded_by_admin and not request.user.is_admin:
            messages.error(request, "This video was uploaded by an administrator. Please use 'Request Deletion' instead.")
        else:
            messages.error(request, "You do not have permission to delete this video.")
        return redirect('manage_videos')
    
    if request.method == 'POST':
        video.is_active = False  # Soft delete
        video.save()
        messages.success(request, 'Video deleted successfully.')
        return redirect('manage_videos')
        
    return redirect('manage_videos')


@never_cache
@login_required
def request_video_deletion(request, video_id):
    """Request deletion of an admin-uploaded or global video."""
    from apps.videos.deletion_requests import VideoDeletionRequest
    from apps.audit.models import AdminActionLog
    
    video = get_object_or_404(Video, id=video_id)
    
    # Only allow deletion requests for videos that require approval (admin-uploaded or global)
    if not video.requires_deletion_approval():
        messages.error(request, "You can delete this video directly.")
        return redirect('manage_videos')
    
    # Check if user has access to this video
    if video.owner != request.user and not video.is_global:
        messages.error(request, "You do not have access to this video.")
        return redirect('manage_videos')
    
    # Check if there's already ANY existing request (pending, approved, or rejected)
    existing_request = VideoDeletionRequest.objects.filter(
        video=video,
        requested_by=request.user
    ).order_by('-requested_at').first()
    
    # If there's an existing request, show its status instead of creating new one
    if existing_request:
        context = {
            'video': video,
            'existing_request': existing_request,
            'show_status': True
        }
        return render(request, 'dashboard/request_deletion.html', context)
    
    # No existing request - allow new request creation
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        
        try:
            deletion_request = VideoDeletionRequest.objects.create(
                video=video,
                requested_by=request.user,
                reason=reason
            )
            
            # Log action
            AdminActionLog.objects.create(
                admin=None,  # User action, not admin
                action_type="DELETION_REQUESTED",
                target_model="Video",
                target_id=str(video.id),
                description=f"User {request.user.email} requested deletion of '{video.title}'"
            )
            
            messages.success(request, 'Deletion request submitted successfully. An admin will review it.')
            return redirect('manage_videos')
            
        except Exception as e:
            messages.error(request, f'Error submitting request: {str(e)}')
    
    return render(request, 'dashboard/request_deletion.html', {'video': video, 'show_status': False})

@never_cache
@login_required
def upgrade_page(request):
    """Show upgrade options."""
    if request.user.plan.name == 'Premium':
        messages.info(request, "You are already a Premium member!")
        return redirect('user_dashboard')
        
    return render(request, 'dashboard/upgrade.html')


@never_cache
@login_required
def process_payment(request):
    """Simulate payment processing."""
    if request.method != 'POST':
        return redirect('upgrade_page')
        
    if request.user.plan.name == 'Premium':
        return redirect('user_dashboard')
        
    try:
        # 1. Get Premium Plan
        premium_plan = Plan.objects.get(name='Premium')
        
        # 2. Create Invoice (Simulated)
        invoice = Invoice.objects.create(
            user=request.user,
            amount=premium_plan.price,
            status='PAID'
        )
        
        # 3. Create Transaction (Simulated)
        Transaction.objects.create(
            invoice=invoice,
            transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
            gateway='demo_gateway',
            status='SUCCESS'
        )
        
        # 4. Upgrade User
        request.user.plan = premium_plan
        request.user.save()
        
        messages.success(request, "Welcome to Premium! You now have 50GB storage and Cloud uploads.")
        return redirect('user_dashboard')
        
    except Plan.DoesNotExist:
        messages.error(request, "Premium plan configuration missing. Please contact support.")
        return redirect('user_dashboard')
    except Exception as e:
        messages.error(request, f"Payment failed: {str(e)}")
        return redirect('upgrade_page')