"""Vistas de la app registros."""
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.cuentas.models import Usuario
from apps.cuentas.services import requiere_rol

from . import repositories, services
from .forms import ComentarioIdentificacionForm, RegistroForm
from .models import ComentarioIdentificacion, Registro, VotoComentario

_ROLES_APORTAR = (Usuario.Rol.OBSERVADOR, Usuario.Rol.REVISOR, Usuario.Rol.ADMINISTRADOR)
_ROLES_VOTAR = (Usuario.Rol.REVISOR, Usuario.Rol.ADMINISTRADOR)


def avistamientos_publicos(request):
    """RF-26: todos los avistamientos aprobados, del más reciente al más antiguo. Público."""
    registros = repositories.listar_avistamientos_publicos()
    pagina = Paginator(registros, 20).get_page(request.GET.get('pagina'))
    return render(request, 'registros/avistamientos_publicos.html', {'registros': pagina, 'pagina': pagina})


def ranking_observadores(request):
    """Ranking público de observadores por cantidad de avistamientos aprobados."""
    ranking = repositories.ranking_observadores()
    return render(request, 'registros/ranking_observadores.html', {'ranking': ranking})


def exportar_avistamientos_csv(request):
    """Exportación pública del inventario consolidado (fuera del MVP original,
    pedido explícito del 22/08/2026). Los mismos datos que avistamientos_publicos,
    en CSV — sin cuenta, porque no hay nada ahí que no esté ya público."""
    contenido = services.generar_csv_avistamientos()
    respuesta = HttpResponse(contenido, content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = 'attachment; filename="ojo-avizor-avistamientos.csv"'
    return respuesta


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
            return redirect('registros:enviado')
    else:
        form = RegistroForm()
    return render(request, 'registros/registro_crear.html', {'form': form})


@requiere_rol(*_ROLES_APORTAR)
def registro_enviado(request):
    return render(request, 'registros/registro_enviado.html')


@requiere_rol(*_ROLES_APORTAR)
def registro_mis(request):
    estado = request.GET.get('estado')
    if estado not in dict(Registro.Estado.choices):
        estado = None
    registros = repositories.listar_de_usuario(request.user, estado=estado)
    pagina = Paginator(registros, 20).get_page(request.GET.get('pagina'))
    return render(request, 'registros/registro_mis.html', {
        'registros': pagina, 'pagina': pagina, 'estado_actual': estado,
    })


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


@requiere_rol(*_ROLES_APORTAR)
def identificar_listar(request):
    """RF-19, RF-29: registros que piden ayuda de la comunidad para identificar la especie."""
    registros = repositories.listar_para_identificar()
    pagina = Paginator(registros, 12).get_page(request.GET.get('pagina'))
    return render(request, 'registros/identificar_listar.html', {'registros': pagina, 'pagina': pagina})


@requiere_rol(*_ROLES_APORTAR)
def identificar_detalle(request, pk):
    try:
        registro = repositories.obtener_para_identificar(pk)
    except Registro.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = ComentarioIdentificacionForm(request.POST)
        if form.is_valid():
            services.crear_comentario_identificacion(
                registro=registro, usuario=request.user, texto=form.cleaned_data['texto'],
            )
            return redirect('registros:identificar_detalle', pk=pk)
    else:
        form = ComentarioIdentificacionForm()

    return render(request, 'registros/identificar_detalle.html', {
        'registro': registro, 'form': form, 'puede_votar': request.user.rol in _ROLES_VOTAR,
    })


@requiere_rol(*_ROLES_VOTAR)
def identificar_votar_comentario(request, pk):
    comentario = get_object_or_404(ComentarioIdentificacion, pk=pk)
    if request.method == 'POST':
        valor = request.POST.get('valor')
        if valor in dict(VotoComentario.Valor.choices):
            services.votar_comentario(comentario=comentario, usuario=request.user, valor=valor)
    return redirect('registros:identificar_detalle', pk=comentario.registro_id)
