"""Consultas de la app catalogo: listado, búsqueda y ficha de especie."""
from django.db.models import Q

from .models import Especie


def listar_especies():
    return Especie.objects.all().order_by('nombre_cientifico')


def obtener_especie(pk):
    return Especie.objects.prefetch_related('nombres_comunes').get(pk=pk)


_ORDENES_VALIDOS = {
    'nombre': ('nombre_cientifico',),
    'recientes': ('-fecha_creacion',),
    'tamano_asc': ('tamano_cm', 'nombre_cientifico'),
    'tamano_desc': ('-tamano_cm', 'nombre_cientifico'),
}


def buscar_especies(texto, *, familia=None, orden=None, tamano_min=None, tamano_max=None, ordenar='nombre'):
    """Busca por nombre científico, nombres comunes, familia y orden (RF-05), con
    filtros combinables (fuera del MVP original, pedido explícito del 25/08/2026):
    familia y orden taxonómico exactos, rango de tamaño, y una forma de ordenar
    los resultados — antes solo se podía buscar texto libre."""
    especies = Especie.objects.prefetch_related('nombres_comunes')
    if texto:
        especies = especies.filter(
            Q(nombre_cientifico__icontains=texto)
            | Q(nombres_comunes__nombre__icontains=texto)
            | Q(familia__icontains=texto)
            | Q(orden__icontains=texto)
        )
    if familia:
        especies = especies.filter(familia=familia)
    if orden:
        especies = especies.filter(orden=orden)
    if tamano_min is not None:
        especies = especies.filter(tamano_cm__gte=tamano_min)
    if tamano_max is not None:
        especies = especies.filter(tamano_cm__lte=tamano_max)
    return especies.distinct().order_by(*_ORDENES_VALIDOS.get(ordenar, _ORDENES_VALIDOS['nombre']))


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


def listar_ordenes():
    """Órdenes taxonómicos presentes en el catálogo, para el filtro avanzado."""
    return (
        Especie.objects.exclude(orden='')
        .order_by('orden')
        .values_list('orden', flat=True)
        .distinct()
    )


def listar_especies_similares(especie, cantidad=4):
    """Otras especies de la misma familia, para la ficha (RF-04 ampliada, fuera
    del MVP original, pedido explícito del 25/08/2026). Sin familia registrada
    no hay forma confiable de emparentarlas, así que no se muestra nada."""
    if not especie.familia:
        return Especie.objects.none()
    return (
        Especie.objects.filter(familia=especie.familia)
        .exclude(pk=especie.pk)
        .prefetch_related('nombres_comunes')
        .order_by('nombre_cientifico')[:cantidad]
    )
