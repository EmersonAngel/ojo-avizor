"""Settings para producción."""
from .base import *  # noqa: F401,F403
from .base import env, env_bool

DEBUG = False

ALLOWED_HOSTS = [h.strip() for h in env('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip()]

SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
