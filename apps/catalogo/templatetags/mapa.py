"""Mapa mundial inline para el componente de distribución de una especie.

Se incrusta el SVG directamente en el HTML (no con <img>) porque el mapa
de distribución necesita colorear países concretos con JavaScript, y un
<img> no permite alcanzar el DOM interno de un SVG externo. El archivo
pesa ~480 KB sin comprimir; comprime bien con gzip/brotli (geometría muy
repetitiva) y solo se carga en la ficha de especie, nunca en el resto del
sitio — ver docs/identidad-visual.md sobre esta decisión (RNF-01).
"""
from functools import lru_cache

from django import template
from django.contrib.staticfiles.finders import find
from django.utils.safestring import mark_safe

from ..paises import PAISES_DISTRIBUCION

register = template.Library()

_NOMBRES_POR_CODIGO = dict(PAISES_DISTRIBUCION)


@register.filter
def nombres_paises(codigos):
    """Traduce una lista de códigos ISO a sus nombres, para el texto alternativo del mapa."""
    return [str(_NOMBRES_POR_CODIGO.get(codigo, codigo)) for codigo in (codigos or [])]


@register.simple_tag
def lista_paises():
    """Países disponibles para marcar la distribución de una especie, en el formulario de gestión."""
    return PAISES_DISTRIBUCION


@lru_cache(maxsize=1)
def _contenido_mapa():
    ruta = find('catalogo/mapa_mundo.svg')
    with open(ruta, encoding='utf-8') as f:
        contenido = f.read()
    # Quita la declaración XML: no es válida incrustada a mitad de un documento HTML.
    if contenido.startswith('<?xml'):
        contenido = contenido.split('?>', 1)[1]
    contenido = contenido.strip()
    # x-ref para que el componente Alpine (mapa-distribucion.js) alcance este <svg>.
    return contenido.replace('<svg', '<svg x-ref="svg"', 1)


@register.simple_tag
def svg_mapa_mundo():
    return mark_safe(_contenido_mapa())
