"""Formularios de la app registros."""
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Registro


class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = [
            'especie', 'cantidad_individuos', 'sin_identificar', 'departamento', 'municipio', 'lugar',
            'fecha_avistamiento', 'latitud', 'longitud', 'comportamiento', 'codigo_reproductivo',
            'sustrato', 'info_adicional', 'nombre_comun_propuesto',
        ]
        widgets = {
            # El buscador tipo eBird de registro_crear.html maneja este campo
            # como un combobox propio (texto + panel de sugerencias por
            # HTMX): el widget real solo necesita viajar oculto en el POST
            # con el id de la especie elegida.
            'especie': forms.HiddenInput(attrs={'x-ref': 'especieId'}),
            'cantidad_individuos': forms.NumberInput(attrs={'min': 1, 'step': 1}),
            'fecha_avistamiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            # El campo real es un <select> oculto (choices=CODIGOS_CHOICES ya
            # los genera el ModelForm solo): registro_crear.html lo maneja
            # como un grupo de chips de Alpine, no lo dibuja Django.
            'codigo_reproductivo': forms.Select(attrs={'class': 'sr-only', 'x-ref': 'codigoReproductivo'}),
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
        help_texts = {
            'sin_identificar': _(
                'Para que la comunidad pueda ayudarte, cuenta algo de lo que viste '
                '(más abajo) o agrega una foto — o ambos.'
            ),
        }
        labels = {
            'especie': _('Especie (si la identificas)'),
            'cantidad_individuos': _('¿Cuántos viste?'),
            'sin_identificar': _('Pido ayuda para identificarla'),
            'departamento': _('Departamento'),
            'municipio': _('Municipio'),
            'latitud': _('Latitud (opcional, no se publica)'),
            'longitud': _('Longitud (opcional, no se publica)'),
            'nombre_comun_propuesto': _('¿Conoces un nombre local para esta ave? (opcional)'),
            'codigo_reproductivo': _('Código reproductivo'),
        }

    def clean(self):
        """Especie amenazada (UICN, desde Vulnerable) + punto exacto es una
        combinación que no se permite (pedido explícito del 12/09/2026, a
        raíz de curar la ficha de la Tángara multicolor): publicar la
        ubicación exacta de un ave amenazada facilita su captura o su acoso.
        Se valida acá, no en el modelo Registro ni en services.py, porque es
        el mismo formulario el que usa tanto el sitio web
        (registros/views.py) como la app móvil (api_movil/views.py) — una
        sola regla cubre los dos."""
        datos = super().clean()
        especie = datos.get('especie')
        if especie and especie.esta_amenazada and (datos.get('latitud') or datos.get('longitud')):
            raise forms.ValidationError(
                _(
                    '%(especie)s está catalogada como especie amenazada (%(categoria)s) — no se '
                    'permite registrar el punto exacto de un avistamiento para proteger su '
                    'ubicación. Puedes seguir describiendo el lugar en el campo "Lugar", sin '
                    'coordenadas precisas.'
                ),
                params={
                    'especie': especie.nombre_cientifico,
                    'categoria': especie.get_categoria_amenaza_display(),
                },
            )
        return datos


class ComentarioIdentificacionForm(forms.Form):
    texto = forms.CharField(
        label=_('Tu comentario'),
        max_length=1000,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': _('¿Reconoces esta ave? Cuéntanos qué especie crees que es y por qué…'),
        }),
    )
