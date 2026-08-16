"""Vistas de la app curaduria."""
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render

from apps.cuentas.models import Usuario
from apps.cuentas.services import requiere_rol
from apps.registros.models import Registro

from . import repositories, services
from .forms import DevolverForm

_ROLES_REVISION = (Usuario.Rol.REVISOR, Usuario.Rol.ADMINISTRADOR)


@requiere_rol(*_ROLES_REVISION)
def bandeja(request):
    registros = repositories.listar_pendientes()
    pagina = Paginator(registros, 10).get_page(request.GET.get('pagina'))
    return render(request, 'curaduria/bandeja.html', {'registros': pagina, 'pagina': pagina})


@requiere_rol(*_ROLES_REVISION)
def detalle(request, pk):
    try:
        registro = repositories.obtener_pendiente(pk)
    except Registro.DoesNotExist:
        raise Http404
    return render(request, 'curaduria/detalle.html', {'registro': registro})


@requiere_rol(*_ROLES_REVISION)
def aprobar(request, pk):
    try:
        registro = repositories.obtener_pendiente(pk)
    except Registro.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        services.aprobar_registro(registro, revisor=request.user)
        messages.success(request, 'Registro aprobado y publicado en el catálogo.')
    return redirect('curaduria:bandeja')


@requiere_rol(*_ROLES_REVISION)
def devolver(request, pk):
    try:
        registro = repositories.obtener_pendiente(pk)
    except Registro.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = DevolverForm(request.POST)
        if form.is_valid():
            services.devolver_registro(registro, revisor=request.user, motivo=form.cleaned_data['motivo'])
            messages.success(request, 'Registro devuelto a su autor con el motivo indicado.')
            return redirect('curaduria:bandeja')
    else:
        form = DevolverForm()
    return render(request, 'curaduria/devolver.html', {'form': form, 'registro': registro})
