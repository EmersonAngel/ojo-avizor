"""Consultas de la app registros: inventario consolidado (RF-26), avistamientos por especie."""
from django.db.models import Count

from .models import Registro


def listar_de_usuario(usuario, estado=None):
    registros = Registro.objects.filter(usuario=usuario).select_related('especie').order_by('-fecha_envio')
    if estado:
        registros = registros.filter(estado=estado)
    return registros


def obtener_de_usuario(pk, usuario):
    return Registro.objects.select_related('especie').get(pk=pk, usuario=usuario)


def contar_observadores_participantes():
    return Registro.publicados.values('usuario').distinct().count()


def contar_avistamientos_publicados():
    return Registro.publicados.count()


def listar_ultimos_publicados(cantidad=6):
    """Los avistamientos aprobados más recientes, para mostrar actividad de la comunidad."""
    return (
        Registro.publicados.select_related('especie', 'usuario')
        .order_by('-fecha_avistamiento', '-fecha_envio')[:cantidad]
    )


def contar_todos_por_estado():
    """Cuántos registros hay en cada estado, para el panel de administrador."""
    conteos = {estado: 0 for estado, _ in Registro.Estado.choices}
    for fila in Registro.objects.values('estado').annotate(total=Count('id')):
        conteos[fila['estado']] = fila['total']
    return conteos


def contar_por_estado_de_usuario(usuario):
    """Cuántos registros tiene un usuario en cada estado, para su página de cuenta."""
    conteos = {estado: 0 for estado, _ in Registro.Estado.choices}
    filas = Registro.objects.filter(usuario=usuario).values('estado').annotate(total=Count('id'))
    for fila in filas:
        conteos[fila['estado']] = fila['total']
    return conteos


def contar_especies_distintas_de_usuario(usuario):
    """Especies distintas que un usuario ha avistado, contando solo aportes ya aprobados."""
    return (
        Registro.publicados.filter(usuario=usuario, especie__isnull=False)
        .values('especie').distinct().count()
    )
