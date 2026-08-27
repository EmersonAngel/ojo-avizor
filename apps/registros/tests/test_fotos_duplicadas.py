"""La misma foto no debe quedar guardada dos veces en un registro — se
reportó el 25/08/2026 que aparecía repetida en la galería de la especie
cuando el mismo archivo se subía dos veces."""
import io
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from apps.cuentas.models import Usuario
from apps.registros import services
from apps.registros.models import Registro


def _bytes_imagen():
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10)).save(buffer, format='JPEG')
    return buffer.getvalue()


def _archivo(nombre='foto.jpg'):
    return SimpleUploadedFile(nombre, _bytes_imagen(), content_type='image/jpeg')


class FotosDuplicadasTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )

    def test_subir_el_mismo_archivo_dos_veces_solo_guarda_una_foto(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
            fotos=[_archivo(), _archivo()],
        )
        self.assertEqual(registro.fotografias.count(), 1)

    def test_fotos_distintas_se_guardan_ambas(self):
        buffer_distinto = io.BytesIO()
        Image.new('RGB', (20, 20)).save(buffer_distinto, format='JPEG')
        archivo_distinto = SimpleUploadedFile('otra.jpg', buffer_distinto.getvalue(), content_type='image/jpeg')

        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
            fotos=[_archivo(), archivo_distinto],
        )
        self.assertEqual(registro.fotografias.count(), 2)

    def test_corregir_no_duplica_una_foto_ya_existente(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
            fotos=[_archivo()],
        )
        registro.estado = Registro.Estado.DEVUELTO
        registro.save(update_fields=['estado'])

        services.corregir_registro(
            registro, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
            fotos=[_archivo()],
        )
        self.assertEqual(registro.fotografias.count(), 1)
