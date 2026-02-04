"""
API views for plans.
"""

from rest_framework import viewsets, permissions
from .models import Plan
from .serializers import PlanSerializer


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing plans."""
    
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]