"""Consultas de la app catalogo: listado, búsqueda y ficha de especie."""
from django.db.models import Q

from .models import Especie


def listar_especies():
    return Especie.objects.all().order_by('nombre_cientifico')


def obtener_especie(pk):
    return Especie.objects.prefetch_related('nombres_comunes').get(pk=pk)


def buscar_especies(texto):
    """Busca por nombre científico, nombres comunes, familia y orden (RF-05)."""
    especies = Especie.objects.prefetch_related('nombres_comunes').order_by('nombre_cientifico')
    if texto:
        especies = especies.filter(
            Q(nombre_cientifico__icontains=texto)
            | Q(nombres_comunes__nombre__icontains=texto)
            | Q(familia__icontains=texto)
            | Q(orden__icontains=texto)
        ).distinct()
    return especies


def contar_especies():
    return Especie.objects.count()


def listar_recientes(cantidad=4):
    """Las últimas fichas creadas, para invitar a explorar el catálogo desde la portada."""
    return Especie.objects.prefetch_related('nombres_comunes').order_by('-fecha_creacion')[:cantidad]


def listar_familias():
    """Familias presentes en el catálogo, para el filtro rápido del listado público."""
    return (
        Especie.objects.exclude(familia='')
        .order_by('familia')
        .values_list('familia', flat=True)
        .distinct()
    )
