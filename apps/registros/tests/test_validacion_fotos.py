"""Ninguna foto subida tenía límite de tamaño ni validación real de que
fuera una imagen (hallazgo de la revisión de seguridad del 25/08/2026):
un archivo enorme o corrupto llegaba directo a Pillow sin control."""
import io
from datetime import date

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from apps.cuentas.models import Usuario
from apps.registros import services


def _imagen_valida():
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10)).save(buffer, format='JPEG')
    return SimpleUploadedFile('foto.jpg', buffer.getvalue(), content_type='image/jpeg')


class ValidacionFotosTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )

    def test_foto_demasiado_pesada_es_invalida(self):
        archivo = SimpleUploadedFile('foto.jpg', b'0' * (services.TAMANO_MAXIMO_ARCHIVO + 1))
        with self.assertRaises(ValidationError):
            services.comprimir_imagen(archivo)

    def test_archivo_que_no_es_imagen_es_invalido(self):
        archivo = SimpleUploadedFile('foto.jpg', b'esto no es una imagen', content_type='image/jpeg')
        with self.assertRaises(ValidationError):
            services.comprimir_imagen(archivo)

    def test_imagen_valida_se_comprime_sin_error(self):
        comprimida = services.comprimir_imagen(_imagen_valida())
        self.assertTrue(comprimida.name.endswith('.jpg'))

    def test_crear_registro_con_foto_invalida_no_crea_nada(self):
        from apps.registros.models import Registro

        archivo = SimpleUploadedFile('foto.jpg', b'esto no es una imagen', content_type='image/jpeg')
        with self.assertRaises(ValidationError):
            services.crear_registro(
                usuario=self.usuario, especie=None, lugar='Vereda X',
                fecha_avistamiento=date.today(), fotos=[archivo],
            )
        self.assertEqual(Registro.objects.count(), 0)
