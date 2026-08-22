"""Actividad por departamento y municipio (fuera del MVP original, pedido explícito del 22/08/2026)."""
from datetime import date

from django.test import TestCase

from apps.cuentas.models import Usuario
from apps.curaduria import services as servicios_curaduria
from apps.registros import repositories, services


class ActividadPorDepartamentoTests(TestCase):
    def setUp(self):
        self.observador = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )
        self.revisor = Usuario.objects.create_user(
            username='rev1', correo='rev1@example.com', nombre_real='Revisora de Prueba',
            seudonimo='revisora1', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
        )

    def _registrar_aprobado(self, departamento, municipio):
        registro = services.crear_registro(
            usuario=self.observador, especie=None, lugar='Un lugar', fecha_avistamiento=date.today(),
            departamento=departamento, municipio=municipio,
        )
        servicios_curaduria.aprobar_registro(registro, revisor=self.revisor)
        return registro

    def test_sin_registros_no_hay_actividad(self):
        self.assertEqual(repositories.contar_actividad_por_departamento(), [])

    def test_agrupa_por_departamento_y_municipio(self):
        self._registrar_aprobado('Quindío', 'Pijao')
        self._registrar_aprobado('Quindío', 'Pijao')
        self._registrar_aprobado('Quindío', 'Armenia')
        self._registrar_aprobado('Antioquia', 'Medellín')

        actividad = repositories.contar_actividad_por_departamento()
        por_nombre = {d['nombre']: d for d in actividad}

        self.assertEqual(por_nombre['Quindío']['total'], 3)
        self.assertEqual(por_nombre['Antioquia']['total'], 1)
        municipios_quindio = {m['nombre']: m['total'] for m in por_nombre['Quindío']['municipios']}
        self.assertEqual(municipios_quindio, {'Pijao': 2, 'Armenia': 1})

    def test_ordena_departamentos_de_mayor_a_menor_actividad(self):
        self._registrar_aprobado('Antioquia', 'Medellín')
        self._registrar_aprobado('Quindío', 'Pijao')
        self._registrar_aprobado('Quindío', 'Pijao')

        actividad = repositories.contar_actividad_por_departamento()
        self.assertEqual([d['nombre'] for d in actividad], ['Quindío', 'Antioquia'])

    def test_solo_cuenta_avistamientos_aprobados(self):
        services.crear_registro(
            usuario=self.observador, especie=None, lugar='Un lugar', fecha_avistamiento=date.today(),
            departamento='Tolima', municipio='Ibagué',
        )  # queda PENDIENTE, sin aprobar
        self.assertEqual(repositories.contar_actividad_por_departamento(), [])

    def test_registro_usa_quindio_pijao_por_defecto(self):
        registro = services.crear_registro(
            usuario=self.observador, especie=None, lugar='Un lugar', fecha_avistamiento=date.today(),
        )
        self.assertEqual(registro.departamento, 'Quindío')
        self.assertEqual(registro.municipio, 'Pijao')
