"""Servicios de dominio de la app curaduria.

aprobar_registro() y devolver_registro(): validan la transición,
crean la Revision y cambian el estado del Registro, todo en una
transacción (ver docs/arquitectura.md). El revisor no corrige el
contenido (RN-03): estas funciones solo cambian el estado.
"""
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.cuentas.services import notificar_por_correo
from apps.registros.models import Registro

from .models import Revision


class TransicionInvalida(Exception):
    pass


@transaction.atomic
def aprobar_registro(registro, *, revisor):
    if registro.estado != Registro.Estado.PENDIENTE:
        raise TransicionInvalida(_('Solo se puede aprobar un registro PENDIENTE.'))
    registro.estado = Registro.Estado.APROBADO
    registro.save(update_fields=['estado'])
    revision = Revision.objects.create(registro=registro, revisor=revisor, decision=Revision.Decision.APROBADO)
    notificar_por_correo(
        registro.usuario,
        asunto=_('Tu avistamiento fue aprobado'),
        mensaje=_(
            'Tu avistamiento en %(lugar)s (%(fecha)s) fue aprobado y ya aparece en el catálogo público de Ojo Avizor.'
        ) % {'lugar': registro.lugar, 'fecha': registro.fecha_avistamiento},
    )
    return revision


@transaction.atomic
def devolver_registro(registro, *, revisor, motivo):
    if registro.estado != Registro.Estado.PENDIENTE:
        raise TransicionInvalida(_('Solo se puede devolver un registro PENDIENTE.'))
    if not motivo or not motivo.strip():
        raise ValueError(_('El motivo es obligatorio para devolver un registro.'))
    registro.estado = Registro.Estado.DEVUELTO
    registro.save(update_fields=['estado'])
    revision = Revision.objects.create(
        registro=registro, revisor=revisor, decision=Revision.Decision.DEVUELTO, motivo=motivo,
    )
    notificar_por_correo(
        registro.usuario,
        asunto=_('Tu avistamiento fue devuelto'),
        mensaje=_(
            'Tu avistamiento en %(lugar)s (%(fecha)s) fue devuelto para que lo corrijas. Motivo: %(motivo)s'
        ) % {'lugar': registro.lugar, 'fecha': registro.fecha_avistamiento, 'motivo': motivo},
    )
    return revision
