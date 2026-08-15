"""Consultas de la app registros: inventario consolidado (RF-26), avistamientos por especie."""
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
