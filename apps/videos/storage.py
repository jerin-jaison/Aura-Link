"""
Storage abstraction for local and cloud uploads.
"""

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class VideoStorage:
    """Abstraction layer for video storage."""
    
    @staticmethod
    def get_storage(storage_type='local'):
        """Get storage backend based on type."""
        
        if storage_type == 's3' or settings.STORAGE_TYPE == 's3':
            return S3Boto3Storage()
        else:
            return FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'videos'))
    
    @staticmethod
    def save_video(file, filename, storage_type='local'):
        """Save video to storage."""
        
        storage = VideoStorage.get_storage(storage_type)
        path = storage.save(filename, file)
        
        if storage_type == 's3':
            return storage.url(path)
        else:
            return path
    
    @staticmethod
    def delete_video(file_path, storage_type='local'):
        """Delete video from storage."""
        
        storage = VideoStorage.get_storage(storage_type)
        try:
            storage.delete(file_path)
            return True
        except Exception:
            return False