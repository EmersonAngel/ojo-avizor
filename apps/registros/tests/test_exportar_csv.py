"""Exportación CSV del inventario (fuera del MVP original, pedido explícito del 22/08/2026)."""
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.catalogo.models import Especie
from apps.cuentas.models import Usuario
from apps.curaduria import services as servicios_curaduria
from apps.registros import services as servicios_registros


class ExportarAvistamientosCsvTests(TestCase):
    def setUp(self):
        self.observador = Usuario.objects.create_user(
            username='obs1', correo='obs.secreto@example.com', nombre_real='Nombre Real Secreto',
            seudonimo='seudo_publico', password='clave-segura-123',
        )
        self.revisor = Usuario.objects.create_user(
            username='rev1', correo='rev1@example.com', nombre_real='Revisora de Prueba',
            seudonimo='revisora1', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
        )
        self.especie = Especie.objects.create(nombre_cientifico='Ramphocelus flammigerus', creado_por=self.revisor)

        self.pendiente = servicios_registros.crear_registro(
            usuario=self.observador, especie=self.especie, lugar='Vereda Pendiente',
            fecha_avistamiento=date.today(), latitud='4.341234', longitud='-75.691234',
        )
        self.aprobado = servicios_registros.crear_registro(
            usuario=self.observador, especie=self.especie, lugar='Vereda Aprobada',
            fecha_avistamiento=date.today(), latitud='4.351234', longitud='-75.701234',
        )
        servicios_curaduria.aprobar_registro(self.aprobado, revisor=self.revisor)

    def test_no_requiere_sesion(self):
        respuesta = self.client.get(reverse('registros:exportar_csv'))
        self.assertEqual(respuesta.status_code, 200)

    def test_es_un_archivo_csv_descargable(self):
        respuesta = self.client.get(reverse('registros:exportar_csv'))
        self.assertEqual(respuesta['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment', respuesta['Content-Disposition'])

    def test_solo_incluye_avistamientos_aprobados(self):
        respuesta = self.client.get(reverse('registros:exportar_csv'))
        contenido = respuesta.content.decode()
        self.assertIn('Vereda Aprobada', contenido)
        self.assertNotIn('Vereda Pendiente', contenido)

    def test_nunca_expone_coordenadas_nombre_real_ni_correo(self):
        respuesta = self.client.get(reverse('registros:exportar_csv'))
        contenido = respuesta.content.decode()
        self.assertIn('seudo_publico', contenido)
        self.assertNotIn('4.351234', contenido)
        self.assertNotIn('-75.701234', contenido)
        self.assertNotIn('Nombre Real Secreto', contenido)
        self.assertNotIn('obs.secreto@example.com', contenido)
