"""Transiciones de estado del Registro (docs/arquitectura.md, pruebas mínimas exigidas)."""
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.cuentas.models import Usuario
from apps.registros import services
from apps.registros.models import Registro


class TransicionesRegistroTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )

    def test_crear_registro_queda_pendiente(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
        )
        self.assertEqual(registro.estado, Registro.Estado.PENDIENTE)

    def test_enviar_registro_que_ya_no_esta_en_borrador_es_invalido(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
        )
        with self.assertRaises(services.TransicionInvalida):
            services.enviar_registro(registro)

    def test_corregir_registro_que_no_esta_devuelto_es_invalido(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
        )
        with self.assertRaises(services.TransicionInvalida):
            services.corregir_registro(
                registro, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
            )

    def test_corregir_registro_devuelto_vuelve_a_pendiente(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
        )
        registro.estado = Registro.Estado.DEVUELTO
        registro.save(update_fields=['estado'])

        corregido = services.corregir_registro(
            registro, especie=None, lugar='Vereda Y', fecha_avistamiento=date.today(),
        )
        self.assertEqual(corregido.estado, Registro.Estado.PENDIENTE)
        self.assertEqual(corregido.lugar, 'Vereda Y')

    def test_fecha_de_avistamiento_futura_es_invalida(self):
        with self.assertRaises(ValidationError):
            services.crear_registro(
                usuario=self.usuario, especie=None, lugar='Vereda X',
                fecha_avistamiento=date.today() + timedelta(days=1),
            )
