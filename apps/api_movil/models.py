"""Modelos de la app api_movil: autenticación por token para la app nativa.

La app móvil no usa cookies de sesión (no es un navegador), así que se
autentica con un token opaco enviado en el header Authorization — ver
apps/api_movil/auth.py. Sin expiración por ahora: es deuda técnica
deliberada del alcance mínimo, no un descuido.
"""
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


def generar_token():
    return secrets.token_hex(32)


class TokenAcceso(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tokens_acceso',
    )
    token = models.CharField(max_length=64, unique=True, default=generar_token, editable=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultimo_uso = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'token de acceso móvil'
        verbose_name_plural = 'tokens de acceso móvil'

    def __str__(self):
        return f'Token de {self.usuario.seudonimo}'

    def actualizar_uso(self):
        self.fecha_ultimo_uso = timezone.now()
        self.save(update_fields=['fecha_ultimo_uso'])
