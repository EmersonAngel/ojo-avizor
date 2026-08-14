"""Vistas de la app cuentas."""
from django.contrib.auth import login
from django.shortcuts import redirect, render

from . import services
from .forms import RegistroForm


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
