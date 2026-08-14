"""URLs raíz del proyecto."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    # Fuera de i18n_patterns y de STATIC_URL a propósito: el service worker
    # solo puede controlar las rutas bajo la ruta desde la que se sirve.
    path('sw.js', views.service_worker, name='service_worker'),
]

urlpatterns += i18n_patterns(
    path('', RedirectView.as_view(pattern_name='catalogo:publico_listado'), name='inicio'),
    path('cuentas/', include('apps.cuentas.urls')),
    path('catalogo/', include('apps.catalogo.urls')),
    path('registros/', include('apps.registros.urls')),
    path('curaduria/', include('apps.curaduria.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
