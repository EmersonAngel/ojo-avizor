"""Formularios de la app catalogo."""
from django import forms
from django.forms import inlineformset_factory

from .models import Especie, NombreComun


class EspecieForm(forms.ModelForm):
    class Meta:
        model = Especie
        fields = [
            'nombre_cientifico', 'familia', 'orden', 'distribucion',
            'tamano_cm', 'historia_natural', 'dato_curioso', 'foto_referencia',
        ]


NombreComunFormSet = inlineformset_factory(
    Especie,
    NombreComun,
    fields=['nombre', 'region', 'es_local', 'estado'],
    extra=1,
    can_delete=True,
)
