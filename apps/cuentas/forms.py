"""Formularios de la app cuentas."""
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from . import repositories


class RegistroForm(forms.Form):
    # Sin campo de "usuario" aparte: para quien se registra es el mismo dato
    # que el seudónimo (pedido explícito, no se veía la diferencia). El
    # nombre de usuario técnico que exige el modelo se deriva solo del
    # seudónimo en apps/cuentas/services.py:registrar_usuario.
    correo = forms.EmailField(label=_('Correo'))
    nombre_real = forms.CharField(max_length=150, label=_('Nombre real'))
    seudonimo = forms.CharField(max_length=50, label=_('Seudónimo'))
    password1 = forms.CharField(widget=forms.PasswordInput, label=_('Contraseña'))
    password2 = forms.CharField(widget=forms.PasswordInput, label=_('Confirmar contraseña'))
    acepta_notificaciones_correo = forms.BooleanField(
        required=False,
        label=_('Quiero recibir correos con notificaciones de la plataforma (por ejemplo, cuando aprueben o devuelvan uno de mis avistamientos).'),
    )

    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if repositories.existe_correo(correo):
            raise forms.ValidationError(_('Ya existe una cuenta con este correo.'))
        return correo

    def clean_seudonimo(self):
        seudonimo = self.cleaned_data['seudonimo']
        if repositories.existe_seudonimo(seudonimo):
            raise forms.ValidationError(_('Ya existe una cuenta con este seudónimo.'))
        return seudonimo

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Las contraseñas no coinciden.'))
        validate_password(password2)
        return password2
