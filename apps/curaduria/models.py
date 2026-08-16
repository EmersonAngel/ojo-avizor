"""Modelos de la app curaduria: flujo de revisión de Registro.

Ver docs/modelo-datos.md y docs/reglas-negocio.md (RN-03, RN-08). Una
Revision registra cada decisión y no se borra nunca: es la trazabilidad
del proceso.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Revision(models.Model):
    """Decisión de curaduría sobre un Registro (RF-07, RF-08)."""

    class Decision(models.TextChoices):
        APROBADO = 'APROBADO', _('Aprobado')
        DEVUELTO = 'DEVUELTO', _('Devuelto')

    registro = models.ForeignKey(
        'registros.Registro',
        on_delete=models.PROTECT,
        related_name='revisiones',
    )
    revisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='revisiones_realizadas',
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    motivo = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'revisión'
        verbose_name_plural = 'revisiones'
        ordering = ['-fecha']

    def clean(self):
        # RN-08 / RF-08: devolver exige motivo, visible para el autor.
        if self.decision == self.Decision.DEVUELTO and not self.motivo.strip():
            raise ValidationError({'motivo': _('El motivo es obligatorio cuando la decisión es DEVUELTO.')})

    def __str__(self):
        return f'Revisión #{self.pk} — {self.decision} (registro #{self.registro_id})'
