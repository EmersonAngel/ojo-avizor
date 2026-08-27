"""Perfil público de observador y tendencia mensual (fuera del MVP original,
pedido explícito del 25/08/2026)."""
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.catalogo.models import Especie
from apps.cuentas.models import Usuario
from apps.registros import repositories, services


class PerfilObservadorTests(TestCase):
    def setUp(self):
        self.observador = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )
        self.especie = Especie.objects.create(nombre_cientifico='Turdus fuscater', creado_por=self.observador)

    def test_sin_aportes_aprobados_da_404(self):
        respuesta = self.client.get(reverse('registros:observador_perfil', args=[self.observador.pk]))
        self.assertEqual(respuesta.status_code, 404)

    def test_pk_inexistente_da_404(self):
        respuesta = self.client.get(reverse('registros:observador_perfil', args=[99999]))
        self.assertEqual(respuesta.status_code, 404)

    def test_con_aporte_aprobado_se_ve_y_no_expone_datos_reservados(self):
        registro = services.crear_registro(
            usuario=self.observador, especie=self.especie, lugar='Vereda X',
            fecha_avistamiento=date.today(), latitud='4.336000', longitud='-75.699000',
        )
        registro.estado = registro.Estado.APROBADO
        registro.save(update_fields=['estado'])

        respuesta = self.client.get(reverse('registros:observador_perfil', args=[self.observador.pk]))
        self.assertEqual(respuesta.status_code, 200)
        contenido = respuesta.content.decode()
        self.assertIn('seudo1', contenido)
        self.assertNotIn('Observador de Prueba', contenido)
        self.assertNotIn('obs1@example.com', contenido)
        self.assertNotIn('4.336', contenido)
        self.assertNotIn('75.699', contenido)


class TendenciaMensualTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )
        self.especie = Especie.objects.create(nombre_cientifico='Turdus fuscater', creado_por=self.usuario)

    def test_devuelve_una_fila_por_mes_pedido(self):
        filas = repositories.tendencia_mensual(meses=6)
        self.assertEqual(len(filas), 6)

    def test_mes_actual_cuenta_lo_aprobado(self):
        registro = services.crear_registro(
            usuario=self.usuario, especie=self.especie, lugar='Vereda X', fecha_avistamiento=date.today(),
        )
        registro.estado = registro.Estado.APROBADO
        registro.save(update_fields=['estado'])

        filas = repositories.tendencia_mensual(meses=6)
        self.assertEqual(filas[-1]['total'], 1)
        self.assertEqual(filas[-1]['porcentaje'], 100)

    def test_registro_pendiente_no_cuenta(self):
        services.crear_registro(
            usuario=self.usuario, especie=self.especie, lugar='Vereda X', fecha_avistamiento=date.today(),
        )
        filas = repositories.tendencia_mensual(meses=6)
        self.assertEqual(sum(fila['total'] for fila in filas), 0)
