"""Foto destacada de la portada (rediseño del 26/08/2026): la foto más
reciente de un avistamiento ya aprobado."""
import io
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from apps.catalogo.models import Especie
from apps.cuentas.models import Usuario
from apps.registros import repositories, services
from apps.registros.models import Registro


def _archivo():
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10)).save(buffer, format='JPEG')
    return SimpleUploadedFile('foto.jpg', buffer.getvalue(), content_type='image/jpeg')


class FotoDestacadaTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )
        self.especie = Especie.objects.create(nombre_cientifico='Turdus fuscater', creado_por=self.usuario)

    def test_sin_avistamientos_aprobados_no_hay_foto_destacada(self):
        services.crear_registro(
            usuario=self.usuario, especie=self.especie, lugar='Vereda X',
            fecha_avistamiento=date.today(), fotos=[_archivo()],
        )
        self.assertIsNone(repositories.foto_destacada_reciente())

    def test_foto_de_registro_aprobado_es_la_destacada(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=self.especie, lugar='Vereda X',
            fecha_avistamiento=date.today(), fotos=[_archivo()],
        )
        registro.estado = Registro.Estado.APROBADO
        registro.save(update_fields=['estado'])

        destacada = repositories.foto_destacada_reciente()
        self.assertIsNotNone(destacada)
        self.assertEqual(destacada.registro_id, registro.pk)
