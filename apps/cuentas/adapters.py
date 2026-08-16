"""Adaptador de django-allauth para el inicio de sesión con Google.

Google no manda username, seudónimo ni rol — los completa este adaptador
la primera vez que se crea la cuenta (RF-27, RF-10). El resto del flujo
(verificación de correo, conexión con una cuenta existente del mismo
correo) lo maneja allauth con la configuración de config/settings/base.py.
"""
import re

from .models import Usuario
from .repositories import existe_seudonimo, existe_username

try:
    from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
except ImportError:  # pragma: no cover - solo si algún día se quita la dependencia
    DefaultSocialAccountAdapter = object


def _generar_valor_unico(base, existe_fn):
    """Recorta a un largo razonable y agrega un número si ya existe (seudónimo y
    username son unique=True en el modelo)."""
    base = base[:40] or 'observador'
    candidato = base
    sufijo = 1
    while existe_fn(candidato):
        sufijo += 1
        candidato = f'{base}{sufijo}'
    return candidato


class AdaptadorCuentasSociales(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        usuario = super().populate_user(request, sociallogin, data)

        nombre = data.get('name') or usuario.correo
        usuario.nombre_real = nombre[:150]

        base = re.sub(r'[^a-zA-Z0-9_]', '', (usuario.correo or '').split('@')[0]) or 'observador'
        usuario.username = _generar_valor_unico(base, existe_username)
        usuario.seudonimo = _generar_valor_unico(base, existe_seudonimo)

        usuario.rol = Usuario.Rol.OBSERVADOR
        return usuario
