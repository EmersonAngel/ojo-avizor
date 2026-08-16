"""Vistas de la app catalogo."""
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.cuentas.models import Usuario
from apps.cuentas.services import requiere_rol
from apps.registros import repositories as registros_repositories
from apps.registros.models import Registro

from . import repositories, services
from .forms import EspecieForm, NombreComunFormSet
from .models import Especie

_ROLES_GESTION = (Usuario.Rol.REVISOR, Usuario.Rol.ADMINISTRADOR)


def portada(request):
    """Puerta de entrada del sitio: presenta el proyecto antes del catálogo en sí,
    no lo reemplaza (RF-03 sigue viviendo en especie_listar_publico)."""
    contexto = {
        'total_especies': repositories.contar_especies(),
        'total_avistamientos': registros_repositories.contar_avistamientos_publicados(),
        'total_observadores': registros_repositories.contar_observadores_participantes(),
        'familias': repositories.listar_familias(),
        'especies_recientes': repositories.listar_recientes(),
        'ultimos_avistamientos': registros_repositories.listar_ultimos_publicados(),
    }
    return render(request, 'catalogo/portada.html', contexto)


def especie_listar_publico(request):
    """RF-03, RF-05: catálogo público, con búsqueda por nombre científico y común.

    Cuando la petición viene de HTMX (buscador en vivo), responde solo el
    fragmento con los resultados en vez de la página completa.
    """
    query = request.GET.get('q', '').strip()
    especies = repositories.buscar_especies(query)
    if request.headers.get('HX-Request') == 'true':
        # Búsqueda en vivo: sin paginar, para no complicar el intercambio parcial.
        return render(request, 'catalogo/_resultados_especies.html', {'especies': especies, 'query': query})
    pagina = Paginator(especies, 12).get_page(request.GET.get('pagina'))
    contexto = {
        'especies': pagina,
        'pagina': pagina,
        'query': query,
        'familias': repositories.listar_familias(),
        'total_especies': repositories.contar_especies(),
    }
    return render(request, 'catalogo/publico_listado.html', contexto)


def especie_detalle(request, pk):
    """RF-04: ficha completa con sus avistamientos aprobados (nunca coordenadas, RN-06)."""
    especie = get_object_or_404(Especie.objects.prefetch_related('nombres_comunes'), pk=pk)
    avistamientos = (
        Registro.publicados.filter(especie=especie)
        .select_related('usuario')
        .order_by('-fecha_avistamiento')
    )
    return render(request, 'catalogo/publico_detalle.html', {'especie': especie, 'avistamientos': avistamientos})


def inventario(request):
    """RF-26: total de especies, avistamientos y observadores participantes."""
    contexto = {
        'total_especies': repositories.contar_especies(),
        'total_avistamientos': registros_repositories.contar_avistamientos_publicados(),
        'total_observadores': registros_repositories.contar_observadores_participantes(),
    }
    return render(request, 'catalogo/inventario.html', contexto)


@requiere_rol(*_ROLES_GESTION)
def especie_listar(request):
    especies = repositories.listar_especies()
    pagina = Paginator(especies, 20).get_page(request.GET.get('pagina'))
    return render(request, 'catalogo/especie_listar.html', {'especies': pagina, 'pagina': pagina})


@requiere_rol(*_ROLES_GESTION)
def especie_crear(request):
    if request.method == 'POST':
        form = EspecieForm(request.POST, request.FILES)
        formset = NombreComunFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            services.guardar_especie(especie_form=form, nombres_formset=formset, creado_por=request.user)
            messages.success(request, 'Ficha creada.')
            return redirect('catalogo:especie_listar')
    else:
        form = EspecieForm()
        formset = NombreComunFormSet()
    return render(request, 'catalogo/especie_formulario.html', {
        'form': form, 'formset': formset, 'accion': 'Crear ficha',
    })


@requiere_rol(*_ROLES_GESTION)
def especie_editar(request, pk):
    especie = repositories.obtener_especie(pk)
    if request.method == 'POST':
        form = EspecieForm(request.POST, request.FILES, instance=especie)
        formset = NombreComunFormSet(request.POST, instance=especie)
        if form.is_valid() and formset.is_valid():
            services.guardar_especie(especie_form=form, nombres_formset=formset, creado_por=request.user)
            messages.success(request, 'Ficha actualizada.')
            return redirect('catalogo:especie_listar')
    else:
        form = EspecieForm(instance=especie)
        formset = NombreComunFormSet(instance=especie)
    return render(request, 'catalogo/especie_formulario.html', {
        'form': form, 'formset': formset, 'accion': 'Editar ficha', 'especie': especie,
    })


@requiere_rol(Usuario.Rol.ADMINISTRADOR)
def especie_retirar(request, pk):
    especie = get_object_or_404(repositories.listar_especies(), pk=pk)
    if request.method == 'POST':
        services.retirar_especie(especie)
        messages.success(request, 'Ficha retirada del catálogo.')
    return redirect('catalogo:especie_listar')
