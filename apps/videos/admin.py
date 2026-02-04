from django.contrib import admin
from .models import Video
from .deletion_requests import VideoDeletionRequest

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'storage_type', 'file_size_mb', 'duration_minutes', 'is_active', 'uploaded_by_admin', 'created_at']
    list_filter = ['storage_type', 'is_active', 'format', 'uploaded_by_admin']
    search_fields = ['title', 'owner__email']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(VideoDeletionRequest)
class VideoDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ['video', 'requested_by', 'status', 'requested_at', 'resolved_by']
    list_filter = ['status', 'requested_at']
    search_fields = ['video__title', 'requested_by__email']
    readonly_fields = ['id', 'requested_at', 'resolved_at']
