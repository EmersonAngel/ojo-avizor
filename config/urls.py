"""URLs raíz del proyecto."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('cuentas/', include('apps.cuentas.urls')),
    path('catalogo/', include('apps.catalogo.urls')),
    path('registros/', include('apps.registros.urls')),
    path('curaduria/', include('apps.curaduria.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
