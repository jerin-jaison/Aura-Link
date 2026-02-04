"""
Video API views.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.db import models

from .models import Video
from .serializers import VideoSerializer, VideoUploadSerializer
from .validators import validate_video_upload, extract_video_metadata
from .storage import VideoStorage
from apps.accounts.permissions import IsActiveUser, CanAccessVideo, CanUploadVideo
from apps.tasks.video_tasks import process_video_metadata

import os
import uuid


class VideoViewSet(viewsets.ModelViewSet):
    """ViewSet for video management."""
    
    serializer_class = VideoSerializer
    permission_classes = [IsActiveUser, CanAccessVideo]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Return videos based on user role."""
        if self.request.user.is_admin:
            return Video.objects.all()
        return Video.objects.filter(models.Q(owner=self.request.user) | models.Q(is_global=True), is_active=True)
    
    @method_decorator(ratelimit(key='user', rate='100/h', method='POST'))
    @action(detail=False, methods=['post'], permission_classes=[CanUploadVideo])
    def upload(self, request):
        """Upload a new video."""
        
        serializer = VideoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        video_file = serializer.validated_data['video_file']
        title = serializer.validated_data['title']
        storage_type = serializer.validated_data['storage_type']
        
        # Detect format
        file_ext = os.path.splitext(video_file.name)[1][1:].lower()
        
        try:
            with transaction.atomic():
                # Validate upload
                validate_video_upload(request.user, video_file, file_ext)
                
                # Check cloud upload permission
                if storage_type == 'CLOUD' and not request.user.plan.cloud_upload_allowed:
                    return Response({
                        'error': 'Cloud upload not allowed for your plan'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Generate unique filename
                filename = f"{uuid.uuid4()}.{file_ext}"
                
                # Save file
                if storage_type == 'CLOUD':
                    file_url = VideoStorage.save_video(video_file, filename, 's3')
                    cloud_url = file_url
                    file_path = ''
                else:
                    file_path = VideoStorage.save_video(video_file, filename, 'local')
                    cloud_url = ''
                
                # Create video record
                video = Video.objects.create(
                    owner=request.user,
                    title=title,
                    storage_type=storage_type,
                    file_path=file_path,
                    cloud_url=cloud_url,
                    file_size=video_file.size,
                    format=file_ext
                )
                
                # Trigger background task for metadata extraction
                # If this fails (e.g. broker down), transaction rolls back
                process_video_metadata.delay(str(video.id))
                
                return Response(
                    VideoSerializer(video).data,
                    status=status.HTTP_201_CREATED
                )
        
        except Exception as e:
            # Delete file if we saved it locally or on cloud but DB failed
            # Note: Ideally this should be more robust, but for now we focus on DB integrity
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def playlist(self, request):
        """Get user's playlist."""
        videos = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(videos, many=True)
        
        return Response({
            'videos': serializer.data,
            'loop_enabled': request.user.plan.playlist_loop_allowed if request.user.plan else False
        })