"""Vistas de la app cuentas."""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from apps.catalogo import repositories as catalogo_repositories
from apps.registros import repositories as registros_repositories

from . import repositories, services
from .forms import RegistroForm
from .models import SolicitudRevisor, Usuario
from .services import requiere_rol


def registrar(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = services.registrar_usuario(
                username=form.cleaned_data['username'],
                correo=form.cleaned_data['correo'],
                nombre_real=form.cleaned_data['nombre_real'],
                seudonimo=form.cleaned_data['seudonimo'],
                password=form.cleaned_data['password1'],
                acepta_notificaciones_correo=form.cleaned_data['acepta_notificaciones_correo'],
            )
            login(request, usuario)
            return redirect('/')
    else:
        form = RegistroForm()

    return render(request, 'cuentas/usuario_registrar.html', {'form': form})


@login_required
def mi_cuenta(request):
    conteos = registros_repositories.contar_por_estado_de_usuario(request.user)
    especies_distintas = registros_repositories.contar_especies_distintas_de_usuario(request.user)
    total = sum(conteos.values())
    return render(request, 'cuentas/mi_cuenta.html', {
        'conteos': conteos,
        'total_aportes': total,
        'especies_distintas': especies_distintas,
        'racha': registros_repositories.calcular_racha_de_usuario(request.user),
        'solicitud_revisor_pendiente': repositories.obtener_solicitud_revisor_pendiente(request.user),
    })


@login_required
def actualizar_notificaciones(request):
    if request.method == 'POST':
        acepta = bool(request.POST.get('acepta_notificaciones_correo'))
        services.actualizar_preferencia_notificaciones(request.user, acepta=acepta)
        if acepta:
            messages.success(request, _('Vas a recibir correos con notificaciones de la plataforma.'))
        else:
            messages.success(request, _('Ya no vas a recibir correos con notificaciones de la plataforma.'))
    return redirect('cuentas:mi_cuenta')


@login_required
def solicitar_revisor(request):
    if request.method == 'POST':
        try:
            services.solicitar_ser_revisor(request.user, mensaje=request.POST.get('mensaje', '').strip())
            messages.success(request, _('Solicitud enviada. Un administrador la va a revisar.'))
        except services.SolicitudRevisorInvalida as error:
            messages.error(request, str(error))
    return redirect('cuentas:mi_cuenta')


@requiere_rol(Usuario.Rol.ADMINISTRADOR)
def panel_admin(request):
    if request.method == 'POST':
        usuario = repositories.listar_todos().filter(pk=request.POST.get('usuario_id')).first()
        nuevo_rol = request.POST.get('rol')
        if usuario is not None:
            try:
                services.cambiar_rol(usuario, nuevo_rol, quien_cambia=request.user)
                messages.success(request, f'Rol de {usuario.seudonimo} actualizado a {usuario.get_rol_display()}.')
            except services.CambioRolInvalido as error:
                messages.error(request, str(error))
        return redirect('cuentas:panel_admin')

    return render(request, 'cuentas/panel_admin.html', {
        'usuarios': repositories.listar_todos(),
        'usuarios_por_rol': repositories.contar_por_rol(),
        'total_especies': catalogo_repositories.contar_especies(),
        'registros_por_estado': registros_repositories.contar_todos_por_estado(),
        'roles': Usuario.Rol.choices,
        'solicitudes_revisor': repositories.listar_solicitudes_revisor_pendientes(),
    })


@requiere_rol(Usuario.Rol.ADMINISTRADOR)
def solicitud_revisor_aprobar(request, pk):
    solicitud = get_object_or_404(SolicitudRevisor, pk=pk)
    if request.method == 'POST':
        try:
            services.resolver_solicitud_revisor(solicitud, aprobar=True, quien_resuelve=request.user)
            messages.success(request, _('%(seudonimo)s ahora es Revisor.') % {'seudonimo': solicitud.usuario.seudonimo})
        except (services.SolicitudRevisorInvalida, services.CambioRolInvalido) as error:
            messages.error(request, str(error))
    return redirect('cuentas:panel_admin')


@requiere_rol(Usuario.Rol.ADMINISTRADOR)
def solicitud_revisor_rechazar(request, pk):
    solicitud = get_object_or_404(SolicitudRevisor, pk=pk)
    if request.method == 'POST':
        try:
            services.resolver_solicitud_revisor(solicitud, aprobar=False, quien_resuelve=request.user)
            messages.success(request, _('Solicitud de %(seudonimo)s rechazada.') % {'seudonimo': solicitud.usuario.seudonimo})
        except services.SolicitudRevisorInvalida as error:
            messages.error(request, str(error))
    return redirect('cuentas:panel_admin')
