"""Autenticación por token para las vistas de api_movil.

Equivalente no-web de requiere_rol (apps/cuentas/services.py): en vez de
redirigir a la página de login cuando falta autenticación, responde 401
en JSON — un cliente nativo no sabe qué hacer con una redirección HTML.
"""
import functools

from django.http import JsonResponse

from .models import TokenAcceso


def requiere_token(vista):
    @functools.wraps(vista)
    def envoltura(request, *args, **kwargs):
        encabezado = request.headers.get('Authorization', '')
        if not encabezado.startswith('Token '):
            return JsonResponse({'detalle': 'Falta encabezado Authorization.'}, status=401)
        valor = encabezado.removeprefix('Token ').strip()
        try:
            token = TokenAcceso.objects.select_related('usuario').get(token=valor)
        except TokenAcceso.DoesNotExist:
            return JsonResponse({'detalle': 'Token inválido.'}, status=401)
        request.user = token.usuario
        token.actualizar_uso()
        return vista(request, *args, **kwargs)

    return envoltura
