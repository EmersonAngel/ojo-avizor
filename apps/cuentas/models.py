"""Modelos de la app cuentas: usuario y roles.

Ver docs/modelo-datos.md. El rol Visitante no es un registro en base de
datos: es el usuario no autenticado.
"""
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Usuario(AbstractUser):
    """Usuario de la plataforma. Extiende AbstractUser (RF-09, RF-27)."""

    class Rol(models.TextChoices):
        ADMINISTRADOR = 'ADMINISTRADOR', _('Administrador')
        REVISOR = 'REVISOR', _('Revisor')
        OBSERVADOR = 'OBSERVADOR', _('Observador')

    class Estado(models.TextChoices):
        ACTIVO = 'ACTIVO', _('Activo')
        SUSPENDIDO = 'SUSPENDIDO', _('Suspendido')

    # nombre_real: obligatorio, nunca visible en el catálogo público (RN-02).
    nombre_real = models.CharField(max_length=150)
    # correo: identificador de acceso.
    correo = models.EmailField(unique=True)
    # seudonimo: lo único que se muestra públicamente (RN-02, RF-28).
    seudonimo = models.CharField(max_length=50, unique=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.OBSERVADOR)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    # Consentimiento explícito, sin marcar por defecto: se pregunta al crear
    # la cuenta y se puede revocar después desde Mi cuenta. Sin esto no se
    # manda ningún correo de notificación (aprobación de avistamientos,
    # respuesta a la solicitud de revisor, etc.) — ver services.notificar_por_correo.
    acepta_notificaciones_correo = models.BooleanField(default=False)

    USERNAME_FIELD = 'correo'
    EMAIL_FIELD = 'correo'
    REQUIRED_FIELDS = ['username', 'nombre_real', 'seudonimo']

    def __str__(self):
        return self.seudonimo


class SolicitudRevisor(models.Model):
    """Pedido de un Observador para convertirse en Revisor voluntario.

    No cambia el rol por sí sola: un Administrador la resuelve desde el
    panel (ver services.resolver_solicitud_revisor), que es quien de verdad
    aplica el cambio de rol vía services.cambiar_rol.
    """

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', _('Pendiente')
        APROBADA = 'APROBADA', _('Aprobada')
        RECHAZADA = 'RECHAZADA', _('Rechazada')

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_revisor',
    )
    mensaje = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    resuelto_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_revisor_resueltas',
    )

    class Meta:
        verbose_name = 'solicitud de revisor'
        verbose_name_plural = 'solicitudes de revisor'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f'Solicitud de {self.usuario.seudonimo} ({self.estado})'
