"""Vistas propias de config.

service_worker: sirve static/sw.js en la raíz del sitio (RF-23). Un
service worker solo puede controlar las rutas bajo la ruta desde la que
se sirve; si se sirviera desde STATIC_URL solo cubriría /static/, por
eso se expone aquí en /sw.js en vez de dejarlo como archivo estático.
"""
from pathlib import Path

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


def service_worker(request):
    ruta = Path(settings.BASE_DIR) / 'static' / 'sw.js'
    return HttpResponse(ruta.read_text(encoding='utf-8'), content_type='application/javascript')


def condiciones_uso(request):
    return render(request, 'condiciones_uso.html')


def descargar_app(request):
    """Página de descarga de la app móvil nativa (Expo/EAS Build, ver
    app_movil/). El QR se genera acá mismo, en SVG, en vez de pedirlo a un
    servicio externo (api.qrserver.com y similares) — no tiene sentido que
    bajar la app dependa de que un tercero esté en pie, justo cuando el
    público real prueba esto con conexión intermitente en campo.
    """
    qr_svg = None
    if settings.URL_APK_ANDROID:
        imagen = qrcode.make(
            settings.URL_APK_ANDROID,
            image_factory=qrcode.image.svg.SvgPathImage,
            box_size=10,
        )
        qr_svg = imagen.to_string(encoding='unicode')
    return render(request, 'descargar_app.html', {
        'url_apk': settings.URL_APK_ANDROID,
        'qr_svg': qr_svg,
    })
