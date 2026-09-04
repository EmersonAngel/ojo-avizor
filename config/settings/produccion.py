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
# apartado 6: "los costos de operación deben ser sostenibles"). Esto vale
# para los estáticos (CSS/JS propios) en cualquier despliegue: no cambian
# en tiempo de ejecución, quedan listos desde que se construye la imagen.
MIDDLEWARE = [MIDDLEWARE[0], 'whitenoise.middleware.WhiteNoiseMiddleware', *MIDDLEWARE[1:]]

# Los archivos subidos por la gente (fotos de avistamientos) sí son
# distintos: en el despliegue con Docker/VPS (README.md, "Despliegue en
# producción — AWS Lightsail") vive un disco propio y persistente, así
# que el sistema de archivos local alcanza. En el despliegue gratuito
# (README.md, "Despliegue gratuito — Render + Neon + Backblaze B2") el
# contenedor de Render NO tiene disco persistente: cualquier foto guardada
# ahí se perdería en el próximo reinicio o despliegue. Por eso, si hay
# credenciales de Backblaze B2 en el entorno, las fotos van ahí en vez de
# al disco — si no las hay (el otro despliegue), sigue siendo disco local,
# sin tocar nada.
#
# Backblaze B2 y no Cloudflare R2 (pensado primero, cambiado el 4 de
# septiembre): R2 pide una tarjeta de crédito para activarse aunque no
# cobre nada dentro de lo gratis — pedido explícito de evitar eso. B2 es
# compatible con la misma API de S3, así que el cambio es solo de
# credenciales, no de mecanismo.
if env('B2_BUCKET_NAME'):
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'bucket_name': env('B2_BUCKET_NAME'),
                'endpoint_url': env('B2_ENDPOINT_URL'),
                'access_key': env('B2_ACCESS_KEY_ID'),
                'secret_key': env('B2_SECRET_ACCESS_KEY'),
                # A diferencia de R2 (que no tiene regiones, "auto" alcanza),
                # B2 sí exige la región real del bucket — la misma que
                # aparece en B2_ENDPOINT_URL (ej. "us-west-004").
                'region_name': env('B2_REGION'),
                'signature_version': 's3v4',
                # El endpoint de la API (B2_ENDPOINT_URL) no sirve para ver
                # las fotos desde el navegador — hace falta el dominio
                # público del bucket (bucket.s3.region.backblazeb2.com).
                'custom_domain': env('B2_PUBLIC_DOMAIN'),
                # Con dominio público la URL no necesita firma con
                # vencimiento: son fotos de un catálogo público, no
                # archivos privados — que el enlace no caduque nunca.
                'querystring_auth': False,
                'file_overwrite': False,
            },
        },
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }
else:
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }
