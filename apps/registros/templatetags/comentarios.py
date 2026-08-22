"""Filtro para el hilo de comentarios de identificación (RF-19, RF-29)."""
from django import template

register = template.Library()


@register.filter
def voto_de(comentario, usuario):
    """Valor del voto de `usuario` sobre `comentario`, o None si no ha votado.

    No dispara una consulta nueva: recorre los votos ya precargados con
    prefetch_related (ver repositories.obtener_para_identificar).
    """
    if not usuario.is_authenticated:
        return None
    for voto in comentario.votos.all():
        if voto.usuario_id == usuario.id:
            return voto.valor
    return None
