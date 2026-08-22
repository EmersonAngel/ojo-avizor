"""Nombre común propuesto desde el registro (RF-18, pedido explícito del 22/08/2026)."""
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.catalogo.models import Especie, NombreComun
from apps.cuentas.models import Usuario
from apps.curaduria import services as servicios_curaduria
from apps.registros import services as servicios_registros


class AgregarNombrePropuestoTests(TestCase):
    def setUp(self):
        self.observador = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )
        self.revisor = Usuario.objects.create_user(
            username='rev1', correo='rev1@example.com', nombre_real='Revisora de Prueba',
            seudonimo='revisora1', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
        )
        self.especie = Especie.objects.create(nombre_cientifico='Turdus fuscater', creado_por=self.revisor)

    def _registrar(self, *, especie, nombre_comun_propuesto=''):
        return servicios_registros.crear_registro(
            usuario=self.observador, especie=especie, lugar='Vereda X', fecha_avistamiento=date.today(),
            nombre_comun_propuesto=nombre_comun_propuesto,
        )

    def test_agregar_el_nombre_lo_crea_aprobado_y_local(self):
        registro = self._registrar(especie=self.especie, nombre_comun_propuesto='mirla montañera')
        servicios_curaduria.agregar_nombre_propuesto(registro)

        nombre_comun = NombreComun.objects.get(especie=self.especie, nombre='mirla montañera')
        self.assertEqual(nombre_comun.estado, NombreComun.Estado.APROBADO)
        self.assertTrue(nombre_comun.es_local)

        registro.refresh_from_db()
        self.assertTrue(registro.nombre_comun_agregado)

    def test_no_se_puede_agregar_dos_veces(self):
        registro = self._registrar(especie=self.especie, nombre_comun_propuesto='mirla montañera')
        servicios_curaduria.agregar_nombre_propuesto(registro)
        with self.assertRaises(servicios_curaduria.TransicionInvalida):
            servicios_curaduria.agregar_nombre_propuesto(registro)

    def test_sin_nombre_propuesto_falla(self):
        registro = self._registrar(especie=self.especie)
        with self.assertRaises(servicios_curaduria.TransicionInvalida):
            servicios_curaduria.agregar_nombre_propuesto(registro)

    def test_sin_especie_identificada_falla(self):
        registro = self._registrar(especie=None, nombre_comun_propuesto='mirla montañera')
        with self.assertRaises(servicios_curaduria.TransicionInvalida):
            servicios_curaduria.agregar_nombre_propuesto(registro)

    def test_proponer_un_nombre_que_ya_existe_no_lo_duplica(self):
        NombreComun.objects.create(especie=self.especie, nombre='mirla montañera')
        registro = self._registrar(especie=self.especie, nombre_comun_propuesto='mirla montañera')
        servicios_curaduria.agregar_nombre_propuesto(registro)
        self.assertEqual(NombreComun.objects.filter(especie=self.especie, nombre='mirla montañera').count(), 1)

    def test_un_observador_no_puede_agregar_el_nombre(self):
        registro = self._registrar(especie=self.especie, nombre_comun_propuesto='mirla montañera')
        self.client.force_login(self.observador)
        respuesta = self.client.post(reverse('curaduria:agregar_nombre_propuesto', args=[registro.pk]))
        self.assertEqual(respuesta.status_code, 403)
        self.assertFalse(NombreComun.objects.filter(especie=self.especie, nombre='mirla montañera').exists())
