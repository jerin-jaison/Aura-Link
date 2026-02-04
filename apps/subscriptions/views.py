"""
Subscription API views.
"""

from rest_framework import viewsets
from rest_framework.response import Response
from .models import Subscription


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for subscription details."""
    
    def list(self, request):
        """Get current user's subscription."""
        try:
            subscription = Subscription.objects.get(user=request.user)
            return Response({
                'plan': subscription.plan.name if subscription.plan else None,
                'status': subscription.status,
                'end_date': subscription.end_date,
                'days_until_expiry': subscription.days_until_expiry(),
                'in_grace_period': subscription.is_in_grace_period()
            })
        except Subscription.DoesNotExist:
            return Response({'plan': request.user.plan.name if request.user.plan else 'Free'})