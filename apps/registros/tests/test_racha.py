"""Racha de días seguidos registrando (pedido explícito del 22/08/2026)."""
from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone

from apps.cuentas.models import Usuario
from apps.registros import repositories, services


class RachaDeUsuarioTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )

    def _registrar_en(self, dias_atras):
        """Crea un registro y le fuerza la fecha de envío (auto_now_add impide pasarla al crear)."""
        registro = services.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
        )
        momento = timezone.now() - timedelta(days=dias_atras)
        type(registro).objects.filter(pk=registro.pk).update(fecha_envio=momento)
        return registro

    def test_sin_registros_la_racha_es_cero(self):
        self.assertEqual(repositories.calcular_racha_de_usuario(self.usuario), 0)

    def test_registrar_hoy_da_una_racha_de_un_dia(self):
        self._registrar_en(0)
        self.assertEqual(repositories.calcular_racha_de_usuario(self.usuario), 1)

    def test_hoy_y_ayer_suman_dos(self):
        self._registrar_en(0)
        self._registrar_en(1)
        self.assertEqual(repositories.calcular_racha_de_usuario(self.usuario), 2)

    def test_solo_ayer_la_racha_sigue_viva(self):
        self._registrar_en(1)
        self.assertEqual(repositories.calcular_racha_de_usuario(self.usuario), 1)

    def test_un_dia_sin_registrar_rompe_la_racha(self):
        self._registrar_en(3)
        self.assertEqual(repositories.calcular_racha_de_usuario(self.usuario), 0)

    def test_un_hueco_solo_cuenta_el_tramo_consecutivo_mas_reciente(self):
        self._registrar_en(0)
        self._registrar_en(1)
        self._registrar_en(3)  # aislado, con un hueco en el día 2
        self.assertEqual(repositories.calcular_racha_de_usuario(self.usuario), 2)

    def test_dos_registros_el_mismo_dia_cuentan_como_un_solo_dia(self):
        self._registrar_en(0)
        self._registrar_en(0)
        self.assertEqual(repositories.calcular_racha_de_usuario(self.usuario), 1)
