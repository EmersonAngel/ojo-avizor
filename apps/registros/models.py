"""Modelos de la app registros: avistamiento (Capa 2).

Ver docs/modelo-datos.md y docs/reglas-negocio.md (RN-01, RN-06, RN-07).
El campo `estado` nunca se asigna directamente desde una vista: solo un
servicio ejecuta las transiciones válidas.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def validar_fecha_no_futura(valor):
    if valor > timezone.localdate():
        raise ValidationError('La fecha de avistamiento no puede ser futura.')


class RegistroPublicadoManager(models.Manager):
    """Solo expone registros APROBADO. Úsalo para todo el catálogo público (RN-01)."""

    def get_queryset(self):
        return super().get_queryset().filter(estado=Registro.Estado.APROBADO)


class Registro(models.Model):
    """Un avistamiento aportado por un Observador. Entidad central (RF-01)."""

    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        APROBADO = 'APROBADO', 'Aprobado'
        DEVUELTO = 'DEVUELTO', 'Devuelto'

    especie = models.ForeignKey(
        'catalogo.Especie',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registros',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='registros',
    )
    lugar = models.CharField(max_length=200)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fecha_avistamiento = models.DateField(validators=[validar_fecha_no_futura])
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR, db_index=True)
    comportamiento = models.TextField(blank=True)
    sustrato = models.CharField(max_length=150, blank=True)
    info_adicional = models.TextField(blank=True)
    sin_identificar = models.BooleanField(default=False)

    objects = models.Manager()
    publicados = RegistroPublicadoManager()

    class Meta:
        verbose_name = 'registro'
        verbose_name_plural = 'registros'
        ordering = ['-fecha_avistamiento']

    def __str__(self):
        especie = self.especie.nombre_cientifico if self.especie else 'sin identificar'
        return f'{especie} — {self.lugar} ({self.fecha_avistamiento})'


class Fotografia(models.Model):
    """Fotografía asociada a un registro (RF-02). Se comprime en un servicio."""

    registro = models.ForeignKey(Registro, on_delete=models.CASCADE, related_name='fotografias')
    archivo = models.ImageField(upload_to='registros/%Y/%m/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'fotografía'
        verbose_name_plural = 'fotografías'
        ordering = ['-fecha_subida']

    def __str__(self):
        return f'Foto de registro #{self.registro_id}'
