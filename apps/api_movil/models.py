"""Modelos de la app api_movil: autenticación por token para la app nativa.

La app móvil no usa cookies de sesión (no es un navegador), así que se
autentica con un token opaco enviado en el header Authorization — ver
apps/api_movil/auth.py. Sin expiración por ahora: es deuda técnica
deliberada del alcance mínimo, no un descuido.
"""
import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


def generar_token():
    # Ya no se usa como default de ningún campo (ver TokenAcceso.crear) —
    # se conserva porque la migración 0001_initial todavía la referencia
    # para reconstruir el estado histórico del modelo; borrarla rompe
    # `manage.py migrate` en una base de datos nueva.
    return secrets.token_hex(32)


def _hash_token(token_en_claro):
    # Token de alta entropía (32 bytes aleatorios) — no hace falta un hash
    # lento tipo contraseña, un SHA-256 directo ya es impracticable de
    # romper por fuerza bruta.
    return hashlib.sha256(token_en_claro.encode()).hexdigest()


class TokenAcceso(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tokens_acceso',
    )
    # Solo se guarda el hash, nunca el token en claro (hallazgo de la revisión
    # de seguridad del 25/08/2026: antes se guardaba en texto plano — si la
    # base de datos se filtrara alguna vez, cualquiera podría usar cualquier
    # sesión móvil activa directamente). El valor en claro solo existe un
    # instante, al crear el token (ver TokenAcceso.crear) — nunca se persiste.
    token_hash = models.CharField(max_length=64, unique=True, editable=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultimo_uso = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'token de acceso móvil'
        verbose_name_plural = 'tokens de acceso móvil'

    def __str__(self):
        return f'Token de {self.usuario.seudonimo}'

    @classmethod
    def crear(cls, usuario):
        """Genera un token opaco y devuelve (instancia, token_en_claro). El
        valor en claro es lo único que se manda al celular — la base de
        datos solo guarda su hash."""
        token_en_claro = secrets.token_hex(32)
        instancia = cls.objects.create(usuario=usuario, token_hash=_hash_token(token_en_claro))
        return instancia, token_en_claro

    @classmethod
    def obtener_por_token(cls, token_en_claro):
        return cls.objects.select_related('usuario').get(token_hash=_hash_token(token_en_claro))

    def actualizar_uso(self):
        self.fecha_ultimo_uso = timezone.now()
        self.save(update_fields=['fecha_ultimo_uso'])
