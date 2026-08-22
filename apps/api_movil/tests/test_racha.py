"""Endpoint de racha para la app móvil (fuera del MVP original, pedido explícito del 22/08/2026)."""
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.api_movil.models import TokenAcceso
from apps.cuentas.models import Usuario
from apps.registros import services as servicios_registros


class RachaMovilTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )
        self.token = TokenAcceso.objects.create(usuario=self.usuario)

    def test_sin_token_responde_401(self):
        respuesta = self.client.get(reverse('api_movil:racha'))
        self.assertEqual(respuesta.status_code, 401)

    def test_con_token_devuelve_la_racha(self):
        servicios_registros.crear_registro(
            usuario=self.usuario, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
        )
        respuesta = self.client.get(
            reverse('api_movil:racha'), HTTP_AUTHORIZATION=f'Token {self.token.token}',
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {'racha': 1})
