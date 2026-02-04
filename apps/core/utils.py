"""
Shared utility functions.
"""

import magic
from django.core.files.uploadedfile import UploadedFile


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_file_type(file: UploadedFile, allowed_types: list):
    """Validate file type using magic numbers."""
    try:
        file_type = magic.from_buffer(file.read(2048), mime=True)
        file.seek(0)  # Reset file pointer
        
        # Map MIME types to extensions
        mime_map = {
            'video/mp4': 'mp4',
            'video/x-matroska': 'mkv',
            'video/webm': 'webm',
        }
        
        detected_type = mime_map.get(file_type)
        return detected_type in allowed_types
    except Exception:
        return False