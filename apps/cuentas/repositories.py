"""Consultas de la app cuentas. Aísla el ORM del dominio."""
from django.db.models import Count

from .models import Usuario


def listar_todos():
    return Usuario.objects.all().order_by('seudonimo')


def contar_por_rol():
    conteos = {rol: 0 for rol, _ in Usuario.Rol.choices}
    for fila in Usuario.objects.values('rol').annotate(total=Count('id')):
        conteos[fila['rol']] = fila['total']
    return conteos


def existe_correo(correo):
    return Usuario.objects.filter(correo=correo).exists()


def existe_seudonimo(seudonimo):
    return Usuario.objects.filter(seudonimo=seudonimo).exists()


def existe_username(username):
    return Usuario.objects.filter(username=username).exists()
