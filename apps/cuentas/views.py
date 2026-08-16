"""Vistas de la app cuentas."""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.catalogo import repositories as catalogo_repositories
from apps.registros import repositories as registros_repositories

from . import repositories, services
from .forms import RegistroForm
from .models import Usuario
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
    })


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
    })
