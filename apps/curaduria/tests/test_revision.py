"""Flujo de curaduría (docs/arquitectura.md, pruebas mínimas exigidas): RN-01, RN-03, RN-08."""
from datetime import date

from django.test import TestCase

from apps.cuentas.models import Usuario
from apps.curaduria import services as servicios_curaduria
from apps.registros import services as servicios_registros
from apps.registros.models import Registro


class RevisionTests(TestCase):
    def setUp(self):
        self.observador = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )
        self.revisor = Usuario.objects.create_user(
            username='rev1', correo='rev1@example.com', nombre_real='Revisora de Prueba',
            seudonimo='revisora1', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
        )
        self.registro = servicios_registros.crear_registro(
            usuario=self.observador, especie=None, lugar='Vereda X', fecha_avistamiento=date.today(),
        )

    def test_aprobar_registro_pendiente_lo_publica_y_crea_revision(self):
        servicios_curaduria.aprobar_registro(self.registro, revisor=self.revisor)
        self.registro.refresh_from_db()
        self.assertEqual(self.registro.estado, Registro.Estado.APROBADO)
        self.assertEqual(self.registro.revisiones.count(), 1)
        self.assertEqual(self.registro.revisiones.first().decision, 'APROBADO')

    def test_aprobar_un_registro_que_ya_no_esta_pendiente_es_invalido(self):
        servicios_curaduria.aprobar_registro(self.registro, revisor=self.revisor)
        with self.assertRaises(servicios_curaduria.TransicionInvalida):
            servicios_curaduria.aprobar_registro(self.registro, revisor=self.revisor)

    def test_devolver_sin_motivo_falla(self):
        with self.assertRaises(ValueError):
            servicios_curaduria.devolver_registro(self.registro, revisor=self.revisor, motivo='')

    def test_devolver_solo_con_espacios_en_blanco_falla(self):
        with self.assertRaises(ValueError):
            servicios_curaduria.devolver_registro(self.registro, revisor=self.revisor, motivo='   ')

    def test_devolver_con_motivo_cambia_estado_y_conserva_el_motivo(self):
        servicios_curaduria.devolver_registro(self.registro, revisor=self.revisor, motivo='Falta una foto clara')
        self.registro.refresh_from_db()
        self.assertEqual(self.registro.estado, Registro.Estado.DEVUELTO)
        self.assertEqual(self.registro.revisiones.first().motivo, 'Falta una foto clara')
