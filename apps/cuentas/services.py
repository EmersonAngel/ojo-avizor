"""Servicios de dominio de la app cuentas (RF-09, RF-10)."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Usuario


class CambioRolInvalido(Exception):
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
        raise CambioRolInvalido(f'"{nuevo_rol}" no es un rol válido.')
    if usuario.pk == quien_cambia.pk:
        raise CambioRolInvalido('No puedes cambiar tu propio rol.')
    usuario.rol = nuevo_rol
    usuario.full_clean()
    usuario.save(update_fields=['rol'])
    return usuario


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
