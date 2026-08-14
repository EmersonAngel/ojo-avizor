"""Vistas propias de config.

service_worker: sirve static/sw.js en la raíz del sitio (RF-23). Un
service worker solo puede controlar las rutas bajo la ruta desde la que
se sirve; si se sirviera desde STATIC_URL solo cubriría /static/, por
eso se expone aquí en /sw.js en vez de dejarlo como archivo estático.
"""
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse


def service_worker(request):
    ruta = Path(settings.BASE_DIR) / 'static' / 'sw.js'
    return HttpResponse(ruta.read_text(encoding='utf-8'), content_type='application/javascript')
