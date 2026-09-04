"""URLs raíz del proyecto."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

from apps.catalogo import views as catalogo_views

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    # Fuera de i18n_patterns y de STATIC_URL a propósito: el service worker
    # solo puede controlar las rutas bajo la ruta desde la que se sirve.
    path('sw.js', views.service_worker, name='service_worker'),
    # Inicio de sesión con Google (django-allauth): también fuera de
    # i18n_patterns a propósito. El URI de redirección se registra tal
    # cual en Google Cloud Console; si quedara bajo /es/ o /en/ según el
    # idioma activo, cambiaría de URL según la sesión y habría que
    # registrar cada variante por separado.
    path('accounts/', include('allauth.urls')),
    # API mínima para la app móvil nativa (Expo): fuera de i18n_patterns
    # por el mismo motivo que sw.js/accounts/ — un cliente que no es
    # navegador no necesita el prefijo de idioma en la URL.
    path('api-movil/', include('apps.api_movil.urls')),
]

urlpatterns += i18n_patterns(
    # Portada (abrebocas, no el catálogo): apartado nuevo, distinto de
    # catalogo:publico_listado, que sigue siendo la búsqueda/listado en sí.
    path('', catalogo_views.portada, name='inicio'),
    path('condiciones-de-uso/', views.condiciones_uso, name='condiciones_uso'),
    path('app/', views.descargar_app, name='descargar_app'),
    path('cuentas/', include('apps.cuentas.urls')),
    path('catalogo/', include('apps.catalogo.urls')),
    path('registros/', include('apps.registros.urls')),
    path('curaduria/', include('apps.curaduria.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
