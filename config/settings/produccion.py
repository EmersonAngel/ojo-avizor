"""Settings para producción."""
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import SECRET_KEY, env, env_bool, MIDDLEWARE

DEBUG = False

# base.py cae en una clave de desarrollo conocida (está en el repositorio
# público) si DJANGO_SECRET_KEY no está definida — perfectamente razonable
# para desarrollo local, pero en producción dejaría las cookies de sesión y
# los tokens CSRF firmables por cualquiera que haya visto el repo (hallazgo
# de la revisión de seguridad del 25/08/2026). Mejor que el despliegue
# falle al arrancar a que quede así en silencio.
if SECRET_KEY == 'clave-insegura-solo-para-desarrollo-local':
    raise ImproperlyConfigured(
        'Falta la variable de entorno DJANGO_SECRET_KEY en producción. '
        'Genera una nueva y exclusiva para este despliegue — nunca reutilices '
        'la clave de desarrollo del repositorio.'
    )

ALLOWED_HOSTS = [h.strip() for h in env('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip()]

SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# WhiteNoise: sirve los estáticos compilados (collectstatic) directamente
# desde el proceso de Django, sin depender de un nginx aparte — mantiene
# el contenedor autosuficiente y el costo de operación bajo (CLAUDE.md,
# apartado 6: "los costos de operación deben ser sostenibles").
MIDDLEWARE = [MIDDLEWARE[0], 'whitenoise.middleware.WhiteNoiseMiddleware', *MIDDLEWARE[1:]]
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
