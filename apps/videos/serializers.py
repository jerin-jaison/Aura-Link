"""
Video serializers.
"""

from rest_framework import serializers
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for Video model."""
    
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    file_size_mb = serializers.FloatField(read_only=True)
    duration_minutes = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Video
        fields = ['id', 'title', 'storage_type', 'file_path', 'cloud_url',
                  'file_size', 'file_size_mb', 'duration', 'duration_minutes',
                  'format', 'thumbnail_url', 'is_active', 'owner_email', 'created_at']
        read_only_fields = ['id', 'file_path', 'cloud_url', 'thumbnail_url',
                            'file_size', 'duration', 'created_at', 'is_active']


class VideoUploadSerializer(serializers.Serializer):
    """Serializer for video upload."""
    
    title = serializers.CharField(max_length=255)
    video_file = serializers.FileField()
    storage_type = serializers.ChoiceField(choices=['LOCAL', 'CLOUD'], default='LOCAL')