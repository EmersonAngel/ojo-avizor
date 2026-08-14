"""Formularios de la app registros."""
from django import forms

from .models import Registro


class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = [
            'especie', 'sin_identificar', 'lugar', 'fecha_avistamiento',
            'latitud', 'longitud', 'comportamiento', 'sustrato', 'info_adicional',
        ]
        widgets = {
            'fecha_avistamiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'comportamiento': forms.Textarea(attrs={'rows': 2}),
            'info_adicional': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'especie': 'Especie (si la identificas)',
            'sin_identificar': 'Pido ayuda para identificarla',
            'latitud': 'Latitud (opcional, no se publica)',
            'longitud': 'Longitud (opcional, no se publica)',
        }
