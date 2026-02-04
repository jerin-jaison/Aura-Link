"""
Decorator for logging admin actions.
"""

from functools import wraps
from .models import AdminActionLog
from apps.core.utils import get_client_ip


def log_admin_action(action_type, target_model):
    """Decorator to log admin actions."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            
            if request.user.is_authenticated and request.user.is_admin:
                # Extract target ID from kwargs or result
                target_id = kwargs.get('pk') or kwargs.get('id') or 'N/A'
                
                AdminActionLog.objects.create(
                    admin=request.user,
                    action_type=action_type,
                    target_model=target_model,
                    target_id=str(target_id),
                    description=f"{action_type} on {target_model}",
                    ip_address=get_client_ip(request)
                )
            
            return result
        return wrapper
    return decorator