"""Formularios de la app cuentas."""
from django import forms
from django.contrib.auth.password_validation import validate_password

from . import repositories


class RegistroForm(forms.Form):
    username = forms.CharField(max_length=150, label='Usuario')
    correo = forms.EmailField(label='Correo')
    nombre_real = forms.CharField(max_length=150, label='Nombre real')
    seudonimo = forms.CharField(max_length=50, label='Seudónimo')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmar contraseña')

    def clean_username(self):
        username = self.cleaned_data['username']
        if repositories.existe_username(username):
            raise forms.ValidationError('Ya existe una cuenta con este nombre de usuario.')
        return username

    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if repositories.existe_correo(correo):
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return correo

    def clean_seudonimo(self):
        seudonimo = self.cleaned_data['seudonimo']
        if repositories.existe_seudonimo(seudonimo):
            raise forms.ValidationError('Ya existe una cuenta con este seudónimo.')
        return seudonimo

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        validate_password(password2)
        return password2
