"""Pedir ayuda a identificar sin descripción ni foto es irresoluble para la
comunidad (regla pedida el 23/08/2026, tras un aporte real sin ninguno de
los dos)."""
import io
from datetime import date

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from apps.cuentas.models import Usuario
from apps.registros import services
from apps.registros.models import Registro


def _archivo_falso():
    # 1x1 px real, generado con Pillow: services.comprimir_imagen necesita poder abrirlo.
    buffer = io.BytesIO()
    Image.new('RGB', (1, 1)).save(buffer, format='JPEG')
    return SimpleUploadedFile('foto.jpg', buffer.getvalue(), content_type='image/jpeg')


class ValidarPedidoDeAyudaTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )

    def test_sin_identificar_sin_descripcion_ni_foto_es_invalido(self):
        with self.assertRaises(ValidationError):
            services.crear_registro(
                usuario=self.usuario, especie=None, lugar='Vereda X',
                fecha_avistamiento=date.today(), sin_identificar=True,
            )
        self.assertEqual(Registro.objects.count(), 0)

    def test_sin_identificar_con_descripcion_es_valido(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X',
            fecha_avistamiento=date.today(), sin_identificar=True,
            comportamiento='Se posaba en una rama baja cerca del agua.',
        )
        self.assertEqual(registro.estado, Registro.Estado.PENDIENTE)

    def test_sin_identificar_con_foto_es_valido(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X',
            fecha_avistamiento=date.today(), sin_identificar=True,
            fotos=[_archivo_falso()],
        )
        self.assertEqual(registro.fotografias.count(), 1)

    def test_identificada_sin_descripcion_ni_foto_es_valido(self):
        # La regla solo aplica cuando se pide ayuda: si el observador ya
        # identificó la especie, no hace falta sustentar nada.
        from apps.catalogo.models import Especie

        revisor = Usuario.objects.create_user(
            username='rev1', correo='rev1@example.com', nombre_real='Revisor de Prueba',
            seudonimo='seudo-revisor', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
        )
        especie = Especie.objects.create(nombre_cientifico='Turdus fuscater', creado_por=revisor)
        registro = services.crear_registro(
            usuario=self.usuario, especie=especie, lugar='Vereda X',
            fecha_avistamiento=date.today(), sin_identificar=False,
        )
        self.assertEqual(registro.estado, Registro.Estado.PENDIENTE)

    def test_corregir_cuenta_las_fotos_ya_existentes(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X',
            fecha_avistamiento=date.today(), sin_identificar=True,
            fotos=[_archivo_falso()],
        )
        registro.estado = Registro.Estado.DEVUELTO
        registro.save(update_fields=['estado'])

        corregido = services.corregir_registro(
            registro, especie=None, lugar='Vereda Y',
            fecha_avistamiento=date.today(), sin_identificar=True,
        )
        self.assertEqual(corregido.estado, Registro.Estado.PENDIENTE)

    def test_corregir_sin_descripcion_ni_foto_es_invalido(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X',
            fecha_avistamiento=date.today(), sin_identificar=True,
            comportamiento='Se posaba en una rama baja cerca del agua.',
        )
        registro.estado = Registro.Estado.DEVUELTO
        registro.save(update_fields=['estado'])

        with self.assertRaises(ValidationError):
            services.corregir_registro(
                registro, especie=None, lugar='Vereda Y',
                fecha_avistamiento=date.today(), sin_identificar=True,
            )
