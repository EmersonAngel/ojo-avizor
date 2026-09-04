"""Sistema de iconos SVG propio del sitio.

Reemplaza los emoji por trazos geométricos consistentes (estilo lineal,
24x24, sin relleno) para una interfaz más profesional. Sin dependencias
externas ni peticiones adicionales: se generan inline, lo que conviene
para RNF-01 (celulares de gama baja).

Uso en plantillas: {% load iconos %} … {% icono "busqueda" clase="w-5 h-5" %}
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Cada entrada es el contenido interno de un <svg viewBox="0 0 24 24">,
# en estilo trazo (hereda fill="none" stroke="currentColor" del contenedor).
_ICONOS = {
    # Silueta de ave posada, con relleno (excepción deliberada al estilo de
    # trazo: como marca de la casa necesita leerse de un vistazo). La
    # cabeza va levantada por encima del cuerpo (postura de ave, no de
    # pez), con pico fino, cola de plumas angosta a un solo lado y patas
    # visibles — ningún pez tiene patas, es la señal más clara.
    'ave': (
        '<g fill="currentColor">'
        '<ellipse cx="11" cy="13" rx="5.5" ry="4.3"/>'
        '<circle cx="15.8" cy="7.2" r="2.6"/>'
        '<path d="M18.1 6.3L20.6 7.2L18.1 8.4z"/>'
        '<path d="M5.5 15.5L1 12l1.5 6.2z"/>'
        '<path d="M9 17.2v3.3M13 17.4v3.3" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>'
        '</g>'
    ),
    'menu': '<path d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5"/>',
    'cerrar': '<path d="M6 18L18 6M6 6l12 12"/>',
    'sol': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>',
    'luna': '<path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>',
    'libro': '<path d="M12 6.04A9 9 0 006 3.75c-1.1 0-2.15.18-3.13.51v13.5A9 9 0 016 17c2.3 0 4.4.87 6 2.29m0-13.25A9 9 0 0118 3.75c1.1 0 2.15.18 3.13.51v13.5A9 9 0 0018 17a9 9 0 00-6 2.29m0-13.25v13.25"/>',
    'busqueda': '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/>',
    'carpeta': '<path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>',
    'check-circulo': '<circle cx="12" cy="12" r="10"/><path d="M8.5 12.5l2.5 2.5 5-5"/>',
    'usuario': '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.5-7 8-7s8 3 8 7"/>',
    'usuarios': '<circle cx="9" cy="8" r="3.25"/><path d="M2.75 19c0-3.2 2.8-5.75 6.25-5.75S15.25 15.8 15.25 19"/><circle cx="17" cy="9" r="2.75"/><path d="M15.5 13.6c2.9.3 5.25 2.6 5.25 5.4"/>',
    'check': '<path d="M4.5 12.75l6 6 9-13.5"/>',
    'deshacer': '<path d="M9 15L3.5 9.5 9 4"/><path d="M3.5 9.5H15a5.5 5.5 0 010 11h-3"/>',
    'lapiz': '<path d="M16.86 4.49a1.87 1.87 0 112.65 2.65L8.24 18.42l-3.98.88.88-3.98L16.86 4.49z"/>',
    'documento': '<path d="M13 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8l-6-5z"/><path d="M13 3v5h5"/>',
    'wifi-off': '<path d="M2 8.5c2.5-2 5.5-3 8.5-3M13.5 5.5c1.3 0 2.6.2 3.8.6M2 12.5c1.5-1.2 3.2-2 5-2.4M15 10.1c1 .3 2 .8 2.9 1.4M6.5 16c1.6-1.2 3.6-1.7 5.5-1.4M12 20h.01"/><path d="M3 3l18 18"/>',
    'ayuda': '<circle cx="12" cy="12" r="10"/><path d="M9.5 9.2a2.5 2.5 0 014.9.8c0 1.7-2.4 2-2.4 3.5"/><path d="M12 17h.01"/>',
    'ojo': '<path d="M2 12s3.5-6.5 10-6.5S22 12 22 12s-3.5 6.5-10 6.5S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    'ubicacion': '<path d="M12 21s7-6.5 7-11.5A7 7 0 105 9.5C5 14.5 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'brujula': '<circle cx="12" cy="12" r="9"/><path d="M15 9l-2 5-5 2 2-5z"/>',
    'regla': '<rect x="3" y="9" width="18" height="6" rx="1"/><path d="M7 9v3M11 9v3M15 9v3M19 9v3"/>',
    'destello': '<path d="M12 3l1.8 5.4L19 10l-5.2 1.6L12 17l-1.8-5.4L5 10l5.2-1.6L12 3z"/>',
    'grafico': '<path d="M4 21V10M10 21V4M16 21v-8M2 21h20"/>',
    'descarga': '<path d="M12 3v12m-4-4l4 4 4-4"/><path d="M4 17v2a2 2 0 002 2h12a2 2 0 002-2v-2"/>',
    'mas': '<path d="M12 4.5v15M4.5 12h15"/>',
    'menos': '<path d="M4.5 12h15"/>',
    'flecha-izquierda': '<path d="M19 12H5M11 18l-6-6 6-6"/>',
    'flecha-abajo': '<path d="M6 9l6 6 6-6"/>',
    'comentario': '<path d="M4 5.5A1.5 1.5 0 015.5 4h13A1.5 1.5 0 0120 5.5v9a1.5 1.5 0 01-1.5 1.5H10l-4.5 4v-4H5.5A1.5 1.5 0 014 14.5v-9z"/>',
    'pulgar-arriba': '<path d="M7 20h9.3a2 2 0 001.98-1.72l1-7A2 2 0 0017.3 9H13V5a2 2 0 00-2-2l-1 1-3 6.5"/><path d="M7 20V10H4v10h3z"/>',
    'pulgar-abajo': '<path d="M7 4h9.3a2 2 0 011.98 1.72l1 7A2 2 0 0117.3 15H13v4a2 2 0 01-2 2l-1-1-3-6.5"/><path d="M7 4v10H4V4h3z"/>',
    'medalla': '<circle cx="12" cy="8.5" r="5.5"/><path d="M9 13L6.5 21 12 18l5.5 3L15 13"/>',
}


@register.simple_tag
def icono(nombre, clase='w-5 h-5'):
    """Devuelve un <svg> inline. `nombre` debe existir en _ICONOS."""
    contenido = _ICONOS.get(nombre, '')
    return mark_safe(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        f'class="{clase}" aria-hidden="true">{contenido}</svg>'
    )
