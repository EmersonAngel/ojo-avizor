"""Formularios de la app catalogo."""
from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Especie, NombreComun
from .paises import PAISES_DISTRIBUCION


class EspecieForm(forms.ModelForm):
    paises_distribucion = forms.MultipleChoiceField(
        choices=PAISES_DISTRIBUCION,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Distribución'),
        help_text=_('Países donde se encuentra la especie. Se muestran como mapa en la ficha pública.'),
    )

    class Meta:
        model = Especie
        fields = [
            'nombre_cientifico', 'familia', 'orden', 'distribucion', 'paises_distribucion',
            'tamano_cm', 'historia_natural', 'dato_curioso', 'foto_referencia',
        ]
        labels = {
            'nombre_cientifico': _('Nombre científico'),
            'familia': _('Familia'),
            'orden': _('Orden'),
            'distribucion': _('Notas sobre la distribución'),
            'tamano_cm': _('Tamaño (cm)'),
            'historia_natural': _('Historia natural'),
            'dato_curioso': _('Dato curioso'),
            'foto_referencia': _('Foto de referencia'),
        }


NombreComunFormSet = inlineformset_factory(
    Especie,
    NombreComun,
    fields=['nombre', 'region', 'es_local', 'estado'],
    labels={
        'nombre': _('Nombre'),
        'region': _('Región'),
        'es_local': _('Propio del municipio'),
        'estado': _('Estado'),
    },
    extra=1,
    can_delete=True,
)
