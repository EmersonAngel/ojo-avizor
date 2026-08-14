"""Servicios de dominio de la app curaduria.

aprobar_registro() y devolver_registro(): validan la transición,
crean la Revision y cambian el estado del Registro, todo en una
transacción (ver docs/arquitectura.md). El revisor no corrige el
contenido (RN-03): estas funciones solo cambian el estado.
"""
from django.db import transaction

from apps.registros.models import Registro

from .models import Revision


class TransicionInvalida(Exception):
    pass


@transaction.atomic
def aprobar_registro(registro, *, revisor):
    if registro.estado != Registro.Estado.PENDIENTE:
        raise TransicionInvalida('Solo se puede aprobar un registro PENDIENTE.')
    registro.estado = Registro.Estado.APROBADO
    registro.save(update_fields=['estado'])
    return Revision.objects.create(registro=registro, revisor=revisor, decision=Revision.Decision.APROBADO)


@transaction.atomic
def devolver_registro(registro, *, revisor, motivo):
    if registro.estado != Registro.Estado.PENDIENTE:
        raise TransicionInvalida('Solo se puede devolver un registro PENDIENTE.')
    if not motivo or not motivo.strip():
        raise ValueError('El motivo es obligatorio para devolver un registro.')
    registro.estado = Registro.Estado.DEVUELTO
    registro.save(update_fields=['estado'])
    return Revision.objects.create(
        registro=registro, revisor=revisor, decision=Revision.Decision.DEVUELTO, motivo=motivo,
    )
