"""Context processors de la app cuentas."""
from . import repositories
from .models import Usuario


def solicitudes_revisor_pendientes(request):
    """Insignia de solicitudes pendientes en la barra, visible solo para Administrador."""
    if request.user.is_authenticated and request.user.rol == Usuario.Rol.ADMINISTRADOR:
        return {'solicitudes_revisor_pendientes': repositories.contar_solicitudes_revisor_pendientes()}
    return {'solicitudes_revisor_pendientes': 0}
