"""Servicios de dominio de la app cuentas (RF-09, RF-10)."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Usuario


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
