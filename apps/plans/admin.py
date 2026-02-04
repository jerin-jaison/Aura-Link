from django.contrib import admin
from .models import Plan

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'max_videos', 'cloud_upload_allowed', 'playlist_loop_allowed']
    search_fields = ['name']