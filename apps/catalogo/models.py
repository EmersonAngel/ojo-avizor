"""Modelos de la app catalogo: ficha de especie (Capa 1).

Ver docs/modelo-datos.md. Solo Revisor y Administrador crean o editan
fichas; esa regla se aplica en services.py, no aquí.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .paises import CODIGOS_VALIDOS


def validar_paises_distribucion(valor):
    invalidos = set(valor) - CODIGOS_VALIDOS
    if invalidos:
        raise ValidationError(
            _('Código de país no reconocido: %(codigos)s.'),
            params={'codigos': ', '.join(sorted(invalidos))},
        )


class Especie(models.Model):
    """Ficha curada de una especie. Entrada única (RF-15, RF-16)."""

    nombre_cientifico = models.CharField(max_length=150, unique=True)
    familia = models.CharField(max_length=100, blank=True)
    orden = models.CharField(max_length=100, blank=True)
    distribucion = models.TextField(blank=True)
    paises_distribucion = models.JSONField(
        default=list,
        blank=True,
        validators=[validar_paises_distribucion],
    )
    tamano_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    historia_natural = models.TextField(blank=True)
    dato_curioso = models.TextField(blank=True)
    foto_referencia = models.ImageField(upload_to='especies/', blank=True, null=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='especies_creadas',
        db_column='creado_por_id_usuario',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'especie'
        verbose_name_plural = 'especies'
        ordering = ['nombre_cientifico']

    def __str__(self):
        return self.nombre_cientifico


class NombreComun(models.Model):
    """Nombre común de una especie. Una especie admite varios (RF-17)."""

    class Estado(models.TextChoices):
        APROBADO = 'APROBADO', _('Aprobado')
        PROPUESTO = 'PROPUESTO', _('Propuesto')

    especie = models.ForeignKey(Especie, on_delete=models.CASCADE, related_name='nombres_comunes')
    nombre = models.CharField(max_length=100, db_index=True)
    region = models.CharField(max_length=100, blank=True)
    es_local = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.APROBADO)

    class Meta:
        verbose_name = 'nombre común'
        verbose_name_plural = 'nombres comunes'
        constraints = [
            models.UniqueConstraint(fields=['especie', 'nombre'], name='nombre_comun_unico_por_especie'),
        ]
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.especie.nombre_cientifico})'
