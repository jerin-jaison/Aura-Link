"""
Audit log views.
"""

from rest_framework import viewsets
from rest_framework.response import Response
from apps.accounts.permissions import IsAdmin
from .models import AdminActionLog


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for audit logs (admin only)."""
    
    permission_classes = [IsAdmin]
    queryset = AdminActionLog.objects.all()
    
    def list(self, request):
        """List audit logs with filtering."""
        logs = self.get_queryset()[:100]  # Latest 100
        
        data = [{
            'admin': log.admin.email if log.admin else 'System',
            'action': log.action_type,
            'target': f"{log.target_model} ({log.target_id})",
            'description': log.description,
            'ip': log.ip_address,
            'timestamp': log.timestamp
        } for log in logs]
        
        return Response(data)