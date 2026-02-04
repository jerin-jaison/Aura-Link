"""
Custom exception handling.
"""

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Custom DRF exception handler with logging."""
    
    response = drf_exception_handler(exc, context)
    
    if response is not None:
        # Log the error
        logger.error(f"API Exception: {exc}", extra={
            'view': context.get('view'),
            'request': context.get('request'),
        })
        
        # Customize error response
        response.data = {
            'error': str(exc),
            'status_code': response.status_code
        }
    
    return response


class PlanLimitExceeded(Exception):
    """Exception raised when plan limits are exceeded."""
    pass


class FileValidationError(Exception):
    """Exception for file validation errors."""
    pass