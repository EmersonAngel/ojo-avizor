"""Especie amenazada (UICN) bloquea el punto exacto del avistamiento (fuera
del MVP original, pedido explícito del 12/09/2026, a raíz de curar la ficha
de la Tángara multicolor)."""
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.catalogo.models import Especie
from apps.cuentas.models import Usuario
from apps.registros.models import Registro


class EstaAmenazadaModeloTests(TestCase):
    def setUp(self):
        self.autor = Usuario.objects.create_user(
            username='autor1', correo='autor1@example.com', nombre_real='Autora de Prueba',
            seudonimo='autora1', password='clave-segura-123',
        )

    def _especie(self, categoria):
        return Especie.objects.create(
            nombre_cientifico=f'Especie {categoria or "sin-categoria"}',
            categoria_amenaza=categoria,
            creado_por=self.autor,
        )

    def test_vulnerable_en_peligro_y_en_peligro_critico_estan_amenazadas(self):
        for categoria in ('VU', 'EN', 'CR'):
            self.assertTrue(self._especie(categoria).esta_amenazada)

    def test_casi_amenazada_preocupacion_menor_y_sin_categoria_no_bloquean(self):
        for categoria in ('NT', 'LC', 'DD', ''):
            self.assertFalse(self._especie(categoria).esta_amenazada)


class RegistroFormularioEspecieAmenazadaTests(TestCase):
    def setUp(self):
        self.observador = Usuario.objects.create_user(
            username='obs2', correo='obs2@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo2', password='clave-segura-123',
        )
        self.client.force_login(self.observador)
        self.tangara = Especie.objects.create(
            nombre_cientifico='Chlorochrysa nitidissima', categoria_amenaza='VU', creado_por=self.observador,
        )
        self.colibri = Especie.objects.create(
            nombre_cientifico='Colibri coruscans', categoria_amenaza='LC', creado_por=self.observador,
        )

    def _datos_minimos(self, **overrides):
        datos = {
            'lugar': 'Vereda X', 'fecha_avistamiento': date.today().isoformat(),
            'departamento': 'Quindío', 'municipio': 'Pijao', 'cantidad_individuos': '1',
        }
        datos.update(overrides)
        return datos

    def test_especie_amenazada_con_coordenadas_es_invalido(self):
        respuesta = self.client.post(reverse('registros:crear'), self._datos_minimos(
            especie=self.tangara.pk, latitud='4.333', longitud='-75.700',
        ))
        self.assertEqual(respuesta.status_code, 200)
        self.assertFormError(
            respuesta.context['form'], None,
            'Chlorochrysa nitidissima está catalogada como especie amenazada (Vulnerable) — no se '
            'permite registrar el punto exacto de un avistamiento para proteger su ubicación. Puedes '
            'seguir describiendo el lugar en el campo "Lugar", sin coordenadas precisas.',
        )
        self.assertFalse(Registro.objects.exists())

    def test_especie_amenazada_sin_coordenadas_se_puede_registrar(self):
        respuesta = self.client.post(reverse('registros:crear'), self._datos_minimos(especie=self.tangara.pk))
        self.assertRedirects(respuesta, reverse('registros:enviado'))
        registro = Registro.objects.get()
        self.assertEqual(registro.especie, self.tangara)
        self.assertIsNone(registro.latitud)
        self.assertIsNone(registro.longitud)

    def test_especie_no_amenazada_con_coordenadas_se_puede_registrar(self):
        respuesta = self.client.post(reverse('registros:crear'), self._datos_minimos(
            especie=self.colibri.pk, latitud='4.333', longitud='-75.700',
        ))
        self.assertRedirects(respuesta, reverse('registros:enviado'))
        registro = Registro.objects.get()
        self.assertEqual(str(registro.latitud), '4.333000')
