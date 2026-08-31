"""Vistas de la app registros."""
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.catalogo.repositories import buscar_especies
from apps.cuentas.models import Usuario
from apps.cuentas.services import requiere_rol

from . import repositories, services
from .codigos_reproductivos import CODIGOS_REPRODUCTIVOS
from .forms import ComentarioIdentificacionForm, RegistroForm
from .models import ComentarioIdentificacion, Registro, VotoComentario

CANTIDAD_SUGERENCIAS_ESPECIE = 8

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


def observador_perfil(request, pk):
    """Perfil público de un observador (fuera del MVP original, pedido explícito
    del 25/08/2026): seudónimo, aportes aprobados, insignias y sus avistamientos
    ya publicados — nunca nombre real, correo ni coordenadas (RN-02, RN-06).

    Solo existe para quien ya tiene algo publicado: sin eso, no hay nada público
    que mostrar, y exponer la página igual sería una forma de acceder a una
    cuenta que en la práctica todavía no aportó nada al inventario."""
    from apps.cuentas.services import evaluar_hitos

    usuario = get_object_or_404(Usuario, pk=pk)
    aportes_aprobados = repositories.contar_aprobados_de_usuario(usuario)
    if aportes_aprobados == 0:
        raise Http404
    especies_distintas = repositories.contar_especies_distintas_de_usuario(usuario)
    racha = repositories.calcular_racha_de_usuario(usuario)
    return render(request, 'registros/observador_perfil.html', {
        'observador': usuario,
        'aportes_aprobados': aportes_aprobados,
        'especies_distintas': especies_distintas,
        'racha': racha,
        'insignias': evaluar_hitos(
            aportes_aprobados=aportes_aprobados, especies_distintas=especies_distintas, racha=racha,
        ),
        'avistamientos': repositories.listar_avistamientos_publicos_de_usuario(usuario),
    })


def exportar_avistamientos_csv(request):
    """Exportación pública del inventario consolidado (fuera del MVP original,
    pedido explícito del 22/08/2026). Los mismos datos que avistamientos_publicos,
    en CSV — sin cuenta, porque no hay nada ahí que no esté ya público."""
    contenido = services.generar_csv_avistamientos()
    respuesta = HttpResponse(contenido, content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = 'attachment; filename="ojo-avizor-avistamientos.csv"'
    return respuesta


def especie_autocompletar(request):
    """Sugerencias del buscador de especie tipo eBird (fuera del MVP original,
    pedido explícito del 30/08/2026): HTMX pide esto en cada tecla, con
    debounce, y responde un fragmento HTML con hasta 8 especies que calcen
    por nombre científico o nombre común. Público — es la misma información
    que ya se ve sin cuenta en /catalogo/, solo que en formato de sugerencia."""
    texto = request.GET.get('q', '').strip()
    especies = buscar_especies(texto)[:CANTIDAD_SUGERENCIAS_ESPECIE] if texto else []
    return render(request, 'registros/_especie_opciones.html', {'especies': especies, 'texto': texto})


@requiere_rol(*_ROLES_APORTAR)
def registro_crear(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                services.crear_registro(
                    usuario=request.user,
                    fotos=request.FILES.getlist('fotos'),
                    **form.cleaned_data,
                )
                return redirect('registros:enviado')
            except ValidationError as error:
                form.add_error(None, error)
    else:
        form = RegistroForm()
    return render(request, 'registros/registro_crear.html', {
        'form': form, 'codigos_reproductivos': CODIGOS_REPRODUCTIVOS,
    })


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
            try:
                services.corregir_registro(
                    registro,
                    fotos=request.FILES.getlist('fotos'),
                    **form.cleaned_data,
                )
                messages.success(request, 'Registro corregido y reenviado a revisión.')
                return redirect('registros:mis_registros')
            except ValidationError as error:
                form.add_error(None, error)
    else:
        form = RegistroForm(instance=registro)

    ultima_revision = registro.revisiones.first()
    return render(request, 'registros/registro_crear.html', {
        'form': form, 'corrigiendo': True, 'ultima_revision': ultima_revision,
        'codigos_reproductivos': CODIGOS_REPRODUCTIVOS,
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
