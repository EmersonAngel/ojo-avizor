"""Servicios de dominio de la app catalogo.

Creación/edición de fichas de especie y sus nombres comunes (RF-16,
RF-17) y retiro de una ficha (RF-13), restringidas a Revisor y
Administrador (RF-13 exige además que el retiro lo haga Administrador;
esa comprobación de rol vive en el decorador de la vista).
"""
import csv

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Especie, NombreComun


@transaction.atomic
def guardar_especie(*, especie_form, nombres_formset, creado_por):
    """Guarda la ficha de especie junto con sus nombres comunes, en una transacción."""
    especie = especie_form.save(commit=False)
    if especie.pk is None:
        especie.creado_por = creado_por
    especie.save()
    nombres_formset.instance = especie
    nombres_formset.save()
    return especie


def retirar_especie(especie):
    """RF-13: retira una ficha publicada; deja de aparecer en el catálogo."""
    especie.delete()


def agregar_nombre_comun_propuesto(*, especie, nombre):
    """RF-18: agrega a la ficha un nombre local sugerido por la comunidad al
    registrar un avistamiento. Lo decide un Revisor al curar ese registro
    (RN-03) — nunca se agrega solo. es_local=True: es la voz de la gente
    del territorio, la razón de ser del proyecto (CLAUDE.md, apartado 1)."""
    nombre = (nombre or '').strip()
    if not nombre:
        raise ValueError('El nombre propuesto no puede estar vacío.')
    nombre_comun, _creado = NombreComun.objects.get_or_create(
        especie=especie, nombre=nombre,
        defaults={'es_local': True, 'estado': NombreComun.Estado.APROBADO},
    )
    return nombre_comun


@transaction.atomic
def importar_especies_desde_csv(archivo_csv, *, creado_por):
    """RF-14: crea fichas de especie a partir de un CSV.

    Columnas esperadas (cabecera obligatoria): nombre_cientifico (única
    obligatoria), familia, orden, distribucion, tamano_cm,
    historia_natural, dato_curioso, nombres_comunes (varios nombres
    separados por ';'). Las especies cuyo nombre_cientifico ya exista se
    omiten: el importador nunca sobrescribe una ficha ya curada.
    """
    lector = csv.DictReader(archivo_csv)
    creadas, omitidas, errores = [], [], []
    for numero_fila, fila in enumerate(lector, start=2):  # la fila 1 es la cabecera
        nombre_cientifico = (fila.get('nombre_cientifico') or '').strip()
        if not nombre_cientifico:
            errores.append((numero_fila, 'nombre_cientifico vacío'))
            continue
        if Especie.objects.filter(nombre_cientifico=nombre_cientifico).exists():
            omitidas.append(nombre_cientifico)
            continue

        especie = Especie(
            nombre_cientifico=nombre_cientifico,
            familia=(fila.get('familia') or '').strip(),
            orden=(fila.get('orden') or '').strip(),
            distribucion=(fila.get('distribucion') or '').strip(),
            tamano_cm=(fila.get('tamano_cm') or '').strip() or None,
            historia_natural=(fila.get('historia_natural') or '').strip(),
            dato_curioso=(fila.get('dato_curioso') or '').strip(),
            creado_por=creado_por,
        )
        try:
            especie.full_clean()
        except ValidationError as exc:
            errores.append((numero_fila, '; '.join(exc.messages)))
            continue
        especie.save()

        nombres_comunes = (fila.get('nombres_comunes') or '').strip()
        for nombre in filter(None, (n.strip() for n in nombres_comunes.split(';'))):
            NombreComun.objects.create(especie=especie, nombre=nombre)

        creadas.append(nombre_cientifico)

    return {'creadas': creadas, 'omitidas': omitidas, 'errores': errores}
