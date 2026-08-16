"""Servicios de dominio de la app cuentas (RF-09, RF-10)."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import SolicitudRevisor, Usuario


class CambioRolInvalido(Exception):
    pass


class SolicitudRevisorInvalida(Exception):
    pass


def registrar_usuario(*, username, correo, nombre_real, seudonimo, password):
    """Crea una cuenta nueva con rol Observador (RF-09, RF-27)."""
    usuario = Usuario(
        username=username,
        correo=correo,
        nombre_real=nombre_real,
        seudonimo=seudonimo,
        rol=Usuario.Rol.OBSERVADOR,
    )
    usuario.set_password(password)
    usuario.full_clean()
    usuario.save()
    return usuario


def cambiar_rol(usuario, nuevo_rol, *, quien_cambia):
    """Cambia el rol de un usuario (RF-10). Solo lo llama la vista del panel de administrador."""
    if nuevo_rol not in Usuario.Rol.values:
        raise CambioRolInvalido(_('"%(rol)s" no es un rol válido.') % {'rol': nuevo_rol})
    if usuario.pk == quien_cambia.pk:
        raise CambioRolInvalido(_('No puedes cambiar tu propio rol.'))
    usuario.rol = nuevo_rol
    usuario.full_clean()
    usuario.save(update_fields=['rol'])
    return usuario


def solicitar_ser_revisor(usuario, *, mensaje=''):
    """Un Observador pide convertirse en Revisor voluntario.

    Una sola solicitud pendiente por usuario a la vez: evita que alguien
    la reenvíe varias veces mientras espera respuesta del Administrador.
    """
    if usuario.rol != Usuario.Rol.OBSERVADOR:
        raise SolicitudRevisorInvalida(_('Solo un Observador puede solicitar ser revisor.'))
    if SolicitudRevisor.objects.filter(usuario=usuario, estado=SolicitudRevisor.Estado.PENDIENTE).exists():
        raise SolicitudRevisorInvalida(_('Ya tienes una solicitud pendiente de respuesta.'))
    solicitud = SolicitudRevisor(usuario=usuario, mensaje=mensaje)
    solicitud.full_clean()
    solicitud.save()
    return solicitud


def resolver_solicitud_revisor(solicitud, *, aprobar, quien_resuelve):
    """Un Administrador aprueba o rechaza una solicitud (RF-10).

    Aprobar aplica el cambio de rol reutilizando cambiar_rol, para no
    duplicar sus validaciones.
    """
    if solicitud.estado != SolicitudRevisor.Estado.PENDIENTE:
        raise SolicitudRevisorInvalida(_('Esta solicitud ya fue resuelta.'))
    if aprobar:
        cambiar_rol(solicitud.usuario, Usuario.Rol.REVISOR, quien_cambia=quien_resuelve)
    solicitud.estado = SolicitudRevisor.Estado.APROBADA if aprobar else SolicitudRevisor.Estado.RECHAZADA
    solicitud.fecha_resolucion = timezone.now()
    solicitud.resuelto_por = quien_resuelve
    solicitud.full_clean()
    solicitud.save()
    return solicitud


def requiere_rol(*roles):
    """Decorador de vista: exige sesión iniciada y uno de los roles dados (RF-10).

    La jerarquía Administrador ⊃ Revisor ⊃ Observador se expresa listando
    explícitamente los roles permitidos en cada vista que lo use.
    """

    def decorador(vista):
        @login_required
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if request.user.rol not in roles:
                raise PermissionDenied
            return vista(request, *args, **kwargs)

        return envoltura

    return decorador
