"""
Simplified development settings for quick local testing (without PostgreSQL/Redis).
"""

from .base import *

# Remove rate limiting app for testing
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django_ratelimit']

# Debug mode
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Use SQLite for testing (instead of PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'auralink.db',
    }
}

# Disable Celery for quick testing (use synchronous execution)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

#  Disable Redis caching (use local memory cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Disable rate limiting for quick testing
RATELIMIT_ENABLE = False

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable Sentry in development
SENTRY_DSN = None

# Security settings (relaxed for development)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Simplified logging for quick testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

print("[OK] Using simplified development settings (SQLite + No Redis)")
