"""Aviso resumido a revisores (RF-24, pedido explícito del 22/08/2026)."""
from datetime import date

from django.core import mail
from django.test import TestCase

from apps.cuentas.models import Usuario
from apps.curaduria import services as servicios_curaduria
from apps.registros import services as servicios_registros


class ResumenPendientesTests(TestCase):
    def setUp(self):
        self.observador = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123', acepta_notificaciones_correo=True,
        )
        self.revisor_activo = Usuario.objects.create_user(
            username='rev1', correo='rev1@example.com', nombre_real='Revisora Activa',
            seudonimo='revisora1', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
            acepta_notificaciones_correo=True,
        )
        self.revisor_sin_correo = Usuario.objects.create_user(
            username='rev2', correo='rev2@example.com', nombre_real='Revisor Sin Correo',
            seudonimo='revisor2', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
            acepta_notificaciones_correo=False,
        )
        self.admin_activo = Usuario.objects.create_user(
            username='admin1', correo='admin1@example.com', nombre_real='Admin Activo',
            seudonimo='admin1', password='clave-segura-123', rol=Usuario.Rol.ADMINISTRADOR,
            acepta_notificaciones_correo=True,
        )

    def test_sin_pendientes_no_manda_nada(self):
        enviados = servicios_curaduria.enviar_resumen_pendientes_a_revisores()
        self.assertEqual(enviados, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_con_pendientes_avisa_solo_a_revisores_y_administradores_con_correo_activado(self):
        servicios_registros.crear_registro(
            usuario=self.observador, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
        )
        enviados = servicios_curaduria.enviar_resumen_pendientes_a_revisores()
        self.assertEqual(enviados, 2)  # revisor_activo y admin_activo

        destinatarios = {correo for msg in mail.outbox for correo in msg.to}
        self.assertIn(self.revisor_activo.correo, destinatarios)
        self.assertIn(self.admin_activo.correo, destinatarios)
        self.assertNotIn(self.revisor_sin_correo.correo, destinatarios)
        self.assertNotIn(self.observador.correo, destinatarios)

    def test_el_correo_menciona_el_total_de_pendientes(self):
        for _ in range(3):
            servicios_registros.crear_registro(
                usuario=self.observador, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
            )
        servicios_curaduria.enviar_resumen_pendientes_a_revisores()
        self.assertTrue(any('3' in msg.body for msg in mail.outbox))
