"""Consultas de la app curaduria: bandeja de revisión."""
from apps.registros.models import Registro


def listar_pendientes():
    return (
        Registro.objects.filter(estado=Registro.Estado.PENDIENTE)
        .select_related('especie', 'usuario')
        .prefetch_related('fotografias')
        .order_by('fecha_envio')
    )


def obtener_pendiente(pk):
    return (
        Registro.objects.filter(estado=Registro.Estado.PENDIENTE)
        .select_related('especie', 'usuario')
        .prefetch_related('fotografias')
        .get(pk=pk)
    )
