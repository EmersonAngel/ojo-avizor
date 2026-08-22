"""Formularios de la app registros."""
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Registro


class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = [
            'especie', 'sin_identificar', 'departamento', 'municipio', 'lugar', 'fecha_avistamiento',
            'latitud', 'longitud', 'comportamiento', 'sustrato', 'info_adicional',
            'nombre_comun_propuesto',
        ]
        widgets = {
            'fecha_avistamiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'comportamiento': forms.Textarea(attrs={'rows': 2}),
            'info_adicional': forms.Textarea(attrs={'rows': 2}),
            'municipio': forms.TextInput(attrs={'placeholder': _('Por ejemplo: Pijao')}),
            # x-model conecta estos campos con el mapa de mapa-ubicacion.js:
            # marcar el punto en el mapa actualiza estos números, y escribir
            # un número mueve el punto (ver registro_crear.html).
            'latitud': forms.NumberInput(attrs={'step': 'any', 'x-model': 'lat', '@change': 'actualizarDesdeCampos()'}),
            'longitud': forms.NumberInput(attrs={'step': 'any', 'x-model': 'lng', '@change': 'actualizarDesdeCampos()'}),
            'nombre_comun_propuesto': forms.TextInput(attrs={
                'placeholder': _('Por ejemplo: como le dicen en tu vereda…'),
            }),
        }
        labels = {
            'especie': _('Especie (si la identificas)'),
            'sin_identificar': _('Pido ayuda para identificarla'),
            'departamento': _('Departamento'),
            'municipio': _('Municipio'),
            'latitud': _('Latitud (opcional, no se publica)'),
            'longitud': _('Longitud (opcional, no se publica)'),
            'nombre_comun_propuesto': _('¿Conoces un nombre local para esta ave? (opcional)'),
        }


class ComentarioIdentificacionForm(forms.Form):
    texto = forms.CharField(
        label=_('Tu comentario'),
        max_length=1000,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': _('¿Reconoces esta ave? Cuéntanos qué especie crees que es y por qué…'),
        }),
    )
