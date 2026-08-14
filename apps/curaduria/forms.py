"""Formularios de la app curaduria."""
from django import forms


class DevolverForm(forms.Form):
    motivo = forms.CharField(
        label='Motivo de la devolución',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
    )
