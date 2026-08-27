"""Modelos de la app registros: avistamiento (Capa 2).

Ver docs/modelo-datos.md y docs/reglas-negocio.md (RN-01, RN-06, RN-07).
El campo `estado` nunca se asigna directamente desde una vista: solo un
servicio ejecuta las transiciones válidas.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .colombia import DEPARTAMENTO_POR_DEFECTO, DEPARTAMENTOS, MUNICIPIO_POR_DEFECTO


def validar_fecha_no_futura(valor):
    if valor > timezone.localdate():
        raise ValidationError(_('La fecha de avistamiento no puede ser futura.'))


class RegistroPublicadoManager(models.Manager):
    """Solo expone registros APROBADO. Úsalo para todo el catálogo público (RN-01)."""

    def get_queryset(self):
        return super().get_queryset().filter(estado=Registro.Estado.APROBADO)


class Registro(models.Model):
    """Un avistamiento aportado por un Observador. Entidad central (RF-01)."""

    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR', _('Borrador')
        PENDIENTE = 'PENDIENTE', _('Pendiente')
        APROBADO = 'APROBADO', _('Aprobado')
        DEVUELTO = 'DEVUELTO', _('Devuelto')

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
    # Región del avistamiento (fuera del MVP original, pedido explícito del
    # 22/08/2026): permite agrupar la actividad del inventario por
    # departamento y municipio, no solo por el texto libre de `lugar`. Por
    # ahora casi todo cae en Quindío/Pijao — el proyecto es de un solo
    # municipio —, pero queda listo si algún día se suman otros lugares.
    departamento = models.CharField(max_length=40, choices=DEPARTAMENTOS, default=DEPARTAMENTO_POR_DEFECTO)
    municipio = models.CharField(max_length=100, default=MUNICIPIO_POR_DEFECTO)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fecha_avistamiento = models.DateField(validators=[validar_fecha_no_futura])
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR, db_index=True)
    comportamiento = models.TextField(blank=True)
    sustrato = models.CharField(max_length=150, blank=True)
    info_adicional = models.TextField(blank=True)
    sin_identificar = models.BooleanField(default=False)
    # RF-18 (fuera del MVP original, construido por pedido explícito del 22/08/2026):
    # nombre local que el observador propone al registrar. No se agrega solo a la
    # ficha de la especie — un Revisor lo decide al curar el registro (RN-03).
    nombre_comun_propuesto = models.CharField(max_length=100, blank=True)
    nombre_comun_agregado = models.BooleanField(default=False)

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
    # Hash del archivo tal como se subió (antes de comprimir), para no guardar
    # la misma foto dos veces en el mismo registro — por ejemplo si el
    # observador la seleccionó dos veces o el formulario se envió doble
    # (hallazgo reportado el 25/08/2026: aparecía repetida en la galería de
    # la especie). Ver apps.registros.services.agregar_fotografia.
    hash_contenido = models.CharField(max_length=64, blank=True, db_index=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'fotografía'
        verbose_name_plural = 'fotografías'
        ordering = ['-fecha_subida']

    def __str__(self):
        return f'Foto de registro #{self.registro_id}'


class ComentarioIdentificacion(models.Model):
    """Comentario de la comunidad para ayudar a identificar un registro `sin_identificar`
    (RF-19, RF-29 — fuera del MVP original, construido por pedido explícito posterior)."""

    registro = models.ForeignKey(Registro, on_delete=models.CASCADE, related_name='comentarios_identificacion')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='comentarios_identificacion',
    )
    texto = models.TextField(max_length=1000)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'comentario de identificación'
        verbose_name_plural = 'comentarios de identificación'
        ordering = ['fecha_creacion']

    def __str__(self):
        return f'Comentario de {self.usuario} en registro #{self.registro_id}'

    @property
    def total_me_gusta(self):
        """No dispara una consulta nueva si `votos` ya viene precargado (prefetch_related)."""
        return sum(1 for voto in self.votos.all() if voto.valor == VotoComentario.Valor.ME_GUSTA)

    @property
    def total_no_me_gusta(self):
        return sum(1 for voto in self.votos.all() if voto.valor == VotoComentario.Valor.NO_ME_GUSTA)


class VotoComentario(models.Model):
    """Voto de un Revisor o Administrador sobre un comentario de identificación: sirve
    para señalar qué sugerencias son creíbles antes de que el revisor decida la especie."""

    class Valor(models.TextChoices):
        ME_GUSTA = 'ME_GUSTA', _('Me gusta')
        NO_ME_GUSTA = 'NO_ME_GUSTA', _('No me gusta')

    comentario = models.ForeignKey(ComentarioIdentificacion, on_delete=models.CASCADE, related_name='votos')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votos_comentarios')
    valor = models.CharField(max_length=15, choices=Valor.choices)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'voto de comentario'
        verbose_name_plural = 'votos de comentario'
        constraints = [
            models.UniqueConstraint(fields=['comentario', 'usuario'], name='un_voto_por_usuario_y_comentario'),
        ]

    def __str__(self):
        return f'{self.usuario} — {self.get_valor_display()} en comentario #{self.comentario_id}'
