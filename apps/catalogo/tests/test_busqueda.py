"""Búsqueda de especies (docs/arquitectura.md, prueba mínima exigida): RF-05."""
from django.test import TestCase

from apps.catalogo.models import Especie, NombreComun
from apps.catalogo.repositories import buscar_especies
from apps.cuentas.models import Usuario


class BusquedaEspeciesTests(TestCase):
    def setUp(self):
        self.revisor = Usuario.objects.create_user(
            username='rev1', correo='rev1@example.com', nombre_real='Revisora de Prueba',
            seudonimo='revisora1', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
        )
        self.especie = Especie.objects.create(
            nombre_cientifico='Ramphocelus flammigerus', creado_por=self.revisor,
        )
        NombreComun.objects.create(especie=self.especie, nombre='Toche')

    def test_busca_por_nombre_cientifico(self):
        self.assertIn(self.especie, buscar_especies('flammigerus'))

    def test_busca_por_nombre_comun(self):
        self.assertIn(self.especie, buscar_especies('toche'))

    def test_no_encuentra_texto_sin_coincidencia(self):
        self.assertNotIn(self.especie, buscar_especies('inexistente-xyz'))
