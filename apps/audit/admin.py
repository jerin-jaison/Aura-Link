from django.contrib import admin
from .models import AdminActionLog

@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'admin', 'target_model', 'target_id', 'timestamp']
    list_filter = ['action_type', 'timestamp']
    search_fields = ['admin__email', 'description']
    readonly_fields = ['admin', 'action_type', 'target_model', 'target_id', 'description', 'ip_address', 'timestamp']