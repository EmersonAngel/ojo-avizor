"""Versión con caché rota a propósito para estáticos, solo para desarrollo.

Causa real de una sesión larga de "no veo los cambios" (31/08/2026):
`runserver`, con STATICFILES_STORAGE de desarrollo, no manda Cache-Control
al servir CSS/JS — solo Last-Modified — así que el navegador aplica su
propia heurística de caché y puede reusar tailwind.css viejo incluso en una
recarga normal, sin volver a pedirlo. Además, el manejo automático de
estáticos de `runserver` intercepta la petición ANTES de que llegue a
cualquier middleware, así que un middleware no puede arreglarlo (se probó y
no funcionó). La solución de verdad, como en cualquier build con hash de
contenido: que la URL cambie cuando cambia el archivo. En producción no
hace falta — ahí ManifestStaticFilesStorage (collectstatic + WhiteNoise) ya
le pone el hash real del contenido al nombre del archivo.

Uso en plantillas: {% load estaticos %} … {% estatico_v "css/tailwind.css" %}
"""
import os

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static as url_estatico

register = template.Library()


@register.simple_tag
def estatico_v(ruta):
    archivo = finders.find(ruta)
    if archivo is None:
        # Producción (u otro archivo que no se encuentra en desarrollo):
        # el comportamiento normal de {% static %} ya es correcto.
        return url_estatico(ruta)
    version = int(os.path.getmtime(archivo))
    return f'{url_estatico(ruta)}?v={version}'
