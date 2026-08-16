"""Modelos de la app cuentas: usuario y roles.

Ver docs/modelo-datos.md. El rol Visitante no es un registro en base de
datos: es el usuario no autenticado.
"""
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

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['username', 'nombre_real', 'seudonimo']

    def __str__(self):
        return self.seudonimo
