"""Formularios de la app curaduria."""
from django import forms
from django.utils.translation import gettext_lazy as _


class DevolverForm(forms.Form):
    motivo = forms.CharField(
        label=_('Motivo de la devolución'),
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
    )
