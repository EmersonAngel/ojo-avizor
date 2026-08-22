"""Servicios de dominio de la app curaduria.

aprobar_registro() y devolver_registro(): validan la transición,
crean la Revision y cambian el estado del Registro, todo en una
transacción (ver docs/arquitectura.md). El revisor no corrige el
contenido (RN-03): estas funciones solo cambian el estado.
"""
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.catalogo import services as catalogo_services
from apps.cuentas.models import Usuario
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


@transaction.atomic
def agregar_nombre_propuesto(registro):
    """RF-18: agrega a la ficha el nombre local que el observador propuso al
    registrar, y marca el registro para que el botón no vuelva a aparecer."""
    if not registro.nombre_comun_propuesto or registro.nombre_comun_agregado:
        raise TransicionInvalida(_('Este registro no tiene un nombre propuesto pendiente de agregar.'))
    if registro.especie is None:
        raise TransicionInvalida(_('No se puede agregar un nombre común sin una especie identificada.'))
    nombre_comun = catalogo_services.agregar_nombre_comun_propuesto(
        especie=registro.especie, nombre=registro.nombre_comun_propuesto,
    )
    registro.nombre_comun_agregado = True
    registro.save(update_fields=['nombre_comun_agregado'])
    return nombre_comun


def enviar_resumen_pendientes_a_revisores():
    """RF-24 (fuera del MVP original, construido por pedido explícito del
    22/08/2026): un aviso resumido, no uno por cada registro nuevo — pensado
    para ejecutarse una vez al día vía tarea programada (cron), ver el
    comando de gestión enviar_resumen_revisores. Si no hay nada pendiente,
    no manda nada: un correo en cero no aporta y solo satura."""
    total_pendientes = Registro.objects.filter(estado=Registro.Estado.PENDIENTE).count()
    if total_pendientes == 0:
        return 0

    revisores = Usuario.objects.filter(
        rol__in=(Usuario.Rol.REVISOR, Usuario.Rol.ADMINISTRADOR),
        acepta_notificaciones_correo=True,
    )
    asunto = _('Tienes avistamientos esperando revisión')
    mensaje = _(
        'Hay %(total)s avistamiento(s) pendientes de revisión en la bandeja de Ojo Avizor.'
    ) % {'total': total_pendientes}
    enviados = 0
    for revisor in revisores:
        if notificar_por_correo(revisor, asunto=asunto, mensaje=mensaje):
            enviados += 1
    return enviados
