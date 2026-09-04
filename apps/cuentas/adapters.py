"""Adaptador de django-allauth para el inicio de sesión con Google.

Google no manda username, seudónimo ni rol — los completa este adaptador
la primera vez que se crea la cuenta (RF-27, RF-10). El resto del flujo
(verificación de correo, conexión con una cuenta existente del mismo
correo) lo maneja allauth con la configuración de config/settings/base.py.
"""
from .repositories import existe_seudonimo, existe_username
from .services import generar_valor_unico
from .models import Usuario

try:
    from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
except ImportError:  # pragma: no cover - solo si algún día se quita la dependencia
    DefaultSocialAccountAdapter = object


class AdaptadorCuentasSociales(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        usuario = super().populate_user(request, sociallogin, data)

        nombre = data.get('name') or usuario.correo
        usuario.nombre_real = nombre[:150]

        base = (usuario.correo or '').split('@')[0]
        usuario.username = generar_valor_unico(base, existe_username)
        usuario.seudonimo = generar_valor_unico(base, existe_seudonimo)

        usuario.rol = Usuario.Rol.OBSERVADOR
        return usuario
