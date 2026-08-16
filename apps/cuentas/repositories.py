"""Consultas de la app cuentas. Aísla el ORM del dominio."""
from django.db.models import Count

from .models import SolicitudRevisor, Usuario


def listar_todos():
    return Usuario.objects.all().order_by('seudonimo')


def contar_por_rol():
    conteos = {rol: 0 for rol, _ in Usuario.Rol.choices}
    for fila in Usuario.objects.values('rol').annotate(total=Count('id')):
        conteos[fila['rol']] = fila['total']
    return conteos


def existe_correo(correo):
    return Usuario.objects.filter(correo=correo).exists()


def existe_seudonimo(seudonimo):
    return Usuario.objects.filter(seudonimo=seudonimo).exists()


def existe_username(username):
    return Usuario.objects.filter(username=username).exists()


def listar_solicitudes_revisor_pendientes():
    return (
        SolicitudRevisor.objects.filter(estado=SolicitudRevisor.Estado.PENDIENTE)
        .select_related('usuario')
        .order_by('fecha_solicitud')
    )


def contar_solicitudes_revisor_pendientes():
    return SolicitudRevisor.objects.filter(estado=SolicitudRevisor.Estado.PENDIENTE).count()


def obtener_solicitud_revisor_pendiente(usuario):
    return SolicitudRevisor.objects.filter(usuario=usuario, estado=SolicitudRevisor.Estado.PENDIENTE).first()
