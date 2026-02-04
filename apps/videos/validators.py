"""
Video file validators.
"""

from django.conf import settings
from apps.core.exceptions import FileValidationError, PlanLimitExceeded
import ffmpeg


def validate_video_upload(user, file, format):
    """Validate video upload against plan limits."""
    
    if not user.plan:
        raise PlanLimitExceeded("No active plan")
    
    plan_name = user.plan.name.upper()
    constraints = settings.VIDEO_CONSTRAINTS.get(plan_name, {})
    
    # Check file size
    max_size = constraints.get('max_file_size', 0)
    if file.size > max_size:
        raise FileValidationError(
            f"File size {file.size // (1024*1024)}MB exceeds limit of {max_size // (1024*1024)}MB"
        )
    
    # Check format
    allowed_formats = constraints.get('allowed_formats', [])
    if format.lower() not in allowed_formats:
        raise FileValidationError(
            f"Format {format} not allowed. Allowed: {', '.join(allowed_formats)}"
        )
    
    # Check video count
    can_upload, message = user.can_upload_video(file.size)
    if not can_upload:
        raise PlanLimitExceeded(message)
    
    return True


def extract_video_metadata(file_path):
    """Extract video metadata using FFmpeg."""
    
    try:
        probe = ffmpeg.probe(file_path)
        video_stream = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
            None
        )
        
        if video_stream:
            duration = float(probe['format']['duration'])
            return {
                'duration': int(duration),
                'width': video_stream.get('width'),
                'height': video_stream.get('height'),
                'codec': video_stream.get('codec_name'),
            }
    except Exception as e:
        # Fallback if FFmpeg fails
        return {'duration': 0}
    
    return {'duration': 0}