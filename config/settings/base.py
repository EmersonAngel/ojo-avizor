"""
Settings comunes a todos los entornos.

Las variables sensibles (SECRET_KEY, credenciales de base de datos) se leen
de variables de entorno / archivo .env. Nunca se hardcodean aquí.
"""
from pathlib import Path

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / '.env')


def env(nombre, default=None):
    return os.environ.get(nombre, default)


def env_bool(nombre, default=False):
    valor = os.environ.get(nombre)
    if valor is None:
        return default
    return valor.strip().lower() in ('1', 'true', 'sí', 'si', 'yes')


SECRET_KEY = env('DJANGO_SECRET_KEY', 'clave-insegura-solo-para-desarrollo-local')

AUTH_USER_MODEL = 'cuentas.Usuario'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # exige django-allauth, aunque el sitio sea uno solo.

    'apps.cuentas',
    'apps.catalogo',
    'apps.registros',
    'apps.curaduria',
    'apps.api_movil',

    # Inicio de sesión con Google — ver la nota junto a SOCIALACCOUNT_PROVIDERS
    # más abajo sobre las credenciales.
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'apps.cuentas.context_processors.solicitudes_revisor_pendientes',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# DB_SSLMODE y DB_CHANNEL_BINDING quedan sin poner en desarrollo y en el
# despliegue con Docker/VPS (Postgres corre al lado, sin necesidad de TLS
# entre contenedores) — Neon (despliegue gratuito, ver README.md) sí los
# exige: la cadena de conexión que da Neon trae "sslmode=require" y
# "channel_binding=require" al final, hay que copiar los dos valores al
# .env por separado, no como una sola cadena (ver README.md, sección
# "Despliegue gratuito", donde se explica cómo repartirla).
_opciones_bd = {}
if env('DB_SSLMODE'):
    _opciones_bd['sslmode'] = env('DB_SSLMODE')
if env('DB_CHANNEL_BINDING'):
    _opciones_bd['channel_binding'] = env('DB_CHANNEL_BINDING')

# Base de datos: PostgreSQL vía variables de entorno.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', 'ojo_avizor'),
        'USER': env('DB_USER', 'ojo_avizor'),
        'PASSWORD': env('DB_PASSWORD', ''),
        'HOST': env('DB_HOST', 'localhost'),
        'PORT': env('DB_PORT', '5432'),
        **({'OPTIONS': _opciones_bd} if _opciones_bd else {}),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización — español por defecto, estructura lista para inglés (RNF-13 fuera de alcance).
LANGUAGE_CODE = 'es'
LANGUAGES = [
    ('es', 'Español'),
    ('en', 'English'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'cuentas:iniciar_sesion'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Correo saliente (recuperar contraseña, notificaciones de curaduría — ver
# apps/cuentas/services.py:notificar_por_correo). En desarrollo se imprime
# en la consola (ver EMAIL_BACKEND en desarrollo.py) y estas variables no
# hacen falta. En producción, sin un proveedor SMTP real configurado, el
# envío falla en silencio (fail_silently=True a propósito, para que un
# correo roto no tumbe la aprobación de un registro) — hay que completar
# las variables DJANGO_EMAIL_* en el .env de producción.
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('DJANGO_EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(env('DJANGO_EMAIL_PORT', '587'))
EMAIL_HOST_USER = env('DJANGO_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env('DJANGO_EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('DJANGO_EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL', 'Ojo Avizor <no-responder@ojoavizor.local>')

# Inicio de sesión con Google (django-allauth). Requiere un ID de cliente y
# un secreto de OAuth de un proyecto en Google Cloud Console — ver la guía
# en README.md, sección "Inicio de sesión con Google". Sin esas dos
# variables de entorno, el botón "Continuar con Google" da error al
# usarse, pero el resto del sitio (correo/contraseña) sigue funcionando
# igual: no es una dependencia dura.
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': env('GOOGLE_CLIENT_ID', ''),
            'secret': env('GOOGLE_CLIENT_SECRET', ''),
            'key': '',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
}

# Usuario (apps/cuentas/models.py) usa 'correo' como identificador y no
# tiene un campo 'username' funcional propio (el heredado de AbstractUser
# no se usa para nada en la lógica de negocio) — se lo decimos a allauth
# explícitamente en vez de dejar que asuma los nombres por defecto de
# Django ('email' y 'username').
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'correo'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*']
# Google ya verificó el correo: no tiene sentido que allauth pida verificarlo
# otra vez con un correo propio — sería una fricción extra sin motivo real,
# y el proyecto no tiene SMTP configurado por defecto en desarrollo.
ACCOUNT_EMAIL_VERIFICATION = 'none'

# apps/cuentas/adapters.py completa nombre_real, seudónimo y rol (RF-27,
# RF-10) al crear la cuenta la primera vez: Google no manda esos campos.
SOCIALACCOUNT_ADAPTER = 'apps.cuentas.adapters.AdaptadorCuentasSociales'
# Si alguien ya tiene cuenta por correo/contraseña y entra con Google usando
# el mismo correo, se conecta a esa cuenta en vez de fallar o duplicarla:
# el correo de Google ya viene verificado, así que es una conexión segura.
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_QUERY_EMAIL = True

# Página /app/ (config/views.py:descargar_app) — enlace directo al .apk que
# genera `eas build` (ver app_movil/README o la bitácora): EAS lo aloja en
# un S3 propio con URL pública y estable, no hace falta subirlo a ningún
# lado nuestro. Cambia cada vez que se genera un build nuevo, así que va
# por variable de entorno y no hardcodeado. Vacío hasta el primer build.
URL_APK_ANDROID = env('URL_APK_ANDROID', '')
