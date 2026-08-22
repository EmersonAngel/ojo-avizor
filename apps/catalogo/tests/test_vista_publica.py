"""Vista pública de ficha de especie (docs/arquitectura.md, pruebas mínimas exigidas): RN-01, RN-02, RN-06."""
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.catalogo.models import Especie
from apps.cuentas.models import Usuario
from apps.curaduria import services as servicios_curaduria
from apps.registros import services as servicios_registros
from apps.registros.models import Fotografia, Registro


class VistaPublicaEspecieTests(TestCase):
    def setUp(self):
        self.revisor = Usuario.objects.create_user(
            username='rev1', correo='rev1@example.com', nombre_real='Nombre Real Secreto',
            seudonimo='revisora1', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
        )
        self.observador = Usuario.objects.create_user(
            username='obs1', correo='obs.secreto@example.com', nombre_real='Nombre Real Del Observador',
            seudonimo='seudo_publico', password='clave-segura-123',
        )
        self.especie = Especie.objects.create(
            nombre_cientifico='Ramphocelus flammigerus', creado_por=self.revisor,
        )
        self.registro_pendiente = servicios_registros.crear_registro(
            usuario=self.observador, especie=self.especie, lugar='Vereda Pendiente',
            fecha_avistamiento=date.today(), latitud='4.341234', longitud='-75.691234',
        )
        self.registro_aprobado = servicios_registros.crear_registro(
            usuario=self.observador, especie=self.especie, lugar='Vereda Aprobada',
            fecha_avistamiento=date.today(), latitud='4.351234', longitud='-75.701234',
        )
        servicios_curaduria.aprobar_registro(self.registro_aprobado, revisor=self.revisor)

    def test_manager_publicados_excluye_los_no_aprobados(self):
        self.assertIn(self.registro_aprobado, Registro.publicados.all())
        self.assertNotIn(self.registro_pendiente, Registro.publicados.all())

    def test_ficha_publica_solo_muestra_avistamientos_aprobados(self):
        respuesta = self.client.get(reverse('catalogo:especie_detalle', args=[self.especie.pk]))
        contenido = respuesta.content.decode()
        self.assertIn('Vereda Aprobada', contenido)
        self.assertNotIn('Vereda Pendiente', contenido)

    def test_ficha_publica_no_expone_nombre_real_ni_correo(self):
        respuesta = self.client.get(reverse('catalogo:especie_detalle', args=[self.especie.pk]))
        contenido = respuesta.content.decode()
        self.assertIn('seudo_publico', contenido)
        self.assertNotIn('Nombre Real Del Observador', contenido)
        self.assertNotIn('obs.secreto@example.com', contenido)

    def test_ficha_publica_no_expone_coordenadas(self):
        respuesta = self.client.get(reverse('catalogo:especie_detalle', args=[self.especie.pk]))
        contenido = respuesta.content.decode()
        self.assertNotIn('4.351234', contenido)
        self.assertNotIn('-75.701234', contenido)

    def test_album_de_fotos_solo_muestra_las_de_avistamientos_aprobados(self):
        Fotografia.objects.create(registro=self.registro_pendiente, archivo='registros/2026/08/pendiente.jpg')
        Fotografia.objects.create(registro=self.registro_aprobado, archivo='registros/2026/08/aprobada.jpg')

        respuesta = self.client.get(reverse('catalogo:especie_detalle', args=[self.especie.pk]))
        contenido = respuesta.content.decode()
        self.assertIn('aprobada.jpg', contenido)
        self.assertNotIn('pendiente.jpg', contenido)
