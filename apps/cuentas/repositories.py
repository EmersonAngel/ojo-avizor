"""Consultas de la app cuentas. Aísla el ORM del dominio."""
from .models import Usuario


def existe_correo(correo):
    return Usuario.objects.filter(correo=correo).exists()


def existe_seudonimo(seudonimo):
    return Usuario.objects.filter(seudonimo=seudonimo).exists()


def existe_username(username):
    return Usuario.objects.filter(username=username).exists()
