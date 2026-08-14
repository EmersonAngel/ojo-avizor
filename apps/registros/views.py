"""Vistas de la app registros."""
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render

from apps.cuentas.models import Usuario
from apps.cuentas.services import requiere_rol

from . import repositories, services
from .forms import RegistroForm
from .models import Registro

_ROLES_APORTAR = (Usuario.Rol.OBSERVADOR, Usuario.Rol.REVISOR, Usuario.Rol.ADMINISTRADOR)


@requiere_rol(*_ROLES_APORTAR)
def registro_crear(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            services.crear_registro(
                usuario=request.user,
                fotos=request.FILES.getlist('fotos'),
                **form.cleaned_data,
            )
            messages.success(request, 'Registro enviado. Quedará pendiente de revisión.')
            return redirect('registros:mis_registros')
    else:
        form = RegistroForm()
    return render(request, 'registros/registro_crear.html', {'form': form})


@requiere_rol(*_ROLES_APORTAR)
def registro_mis(request):
    registros = repositories.listar_de_usuario(request.user)
    pagina = Paginator(registros, 20).get_page(request.GET.get('pagina'))
    return render(request, 'registros/registro_mis.html', {'registros': pagina, 'pagina': pagina})


@requiere_rol(*_ROLES_APORTAR)
def registro_corregir(request, pk):
    try:
        registro = repositories.obtener_de_usuario(pk, request.user)
    except Registro.DoesNotExist:
        raise Http404
    if registro.estado != Registro.Estado.DEVUELTO:
        messages.error(request, 'Solo se puede corregir un registro devuelto.')
        return redirect('registros:mis_registros')

    if request.method == 'POST':
        form = RegistroForm(request.POST, instance=registro)
        if form.is_valid():
            services.corregir_registro(
                registro,
                fotos=request.FILES.getlist('fotos'),
                **form.cleaned_data,
            )
            messages.success(request, 'Registro corregido y reenviado a revisión.')
            return redirect('registros:mis_registros')
    else:
        form = RegistroForm(instance=registro)

    ultima_revision = registro.revisiones.first()
    return render(request, 'registros/registro_crear.html', {
        'form': form, 'corrigiendo': True, 'ultima_revision': ultima_revision,
    })
