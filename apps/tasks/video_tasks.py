"""
Celery tasks for video processing.
"""

from celery import shared_task
from apps.videos.models import Video
from apps.videos.validators import extract_video_metadata
import os


@shared_task
def process_video_metadata(video_id):
    """Extract and save video metadata."""
    
    try:
        video = Video.objects.get(id=video_id)
        
        # Get file path
        if video.storage_type == 'LOCAL':
            file_path = os.path.join('media', 'videos', video.file_path)
            
            # Extract metadata
            metadata = extract_video_metadata(file_path)
            
            # Update video
            video.duration = metadata.get('duration', 0)
            video.save()
            
            return f"Processed video {video_id}"
        
        return f"Skipped cloud video {video_id}"
    
    except Video.DoesNotExist:
        return f"Video {video_id} not found"
    except Exception as e:
        return f"Error processing {video_id}: {str(e)}"