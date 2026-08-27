"""Filtros avanzados del catálogo público y especies similares (fuera del
MVP original, pedido explícito del 25/08/2026)."""
from django.test import TestCase
from django.urls import reverse

from apps.catalogo.models import Especie
from apps.catalogo.repositories import buscar_especies, listar_especies_similares
from apps.cuentas.models import Usuario


class FiltrosAvanzadosTests(TestCase):
    def setUp(self):
        self.revisor = Usuario.objects.create_user(
            username='rev1', correo='rev1@example.com', nombre_real='Revisora de Prueba',
            seudonimo='revisora1', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
        )
        self.colibri = Especie.objects.create(
            nombre_cientifico='Colibri coruscans', familia='Trochilidae', orden='Apodiformes',
            tamano_cm=12, creado_por=self.revisor,
        )
        self.tominejo_gigante = Especie.objects.create(
            nombre_cientifico='Patagona gigas', familia='Trochilidae', orden='Apodiformes',
            tamano_cm=22, creado_por=self.revisor,
        )
        self.mirla = Especie.objects.create(
            nombre_cientifico='Turdus fuscater', familia='Turdidae', orden='Passeriformes',
            tamano_cm=28, creado_por=self.revisor,
        )

    def test_filtra_por_familia(self):
        resultado = buscar_especies('', familia='Trochilidae')
        self.assertCountEqual(resultado, [self.colibri, self.tominejo_gigante])

    def test_filtra_por_orden(self):
        resultado = buscar_especies('', orden='Passeriformes')
        self.assertCountEqual(resultado, [self.mirla])

    def test_filtra_por_rango_de_tamano(self):
        resultado = buscar_especies('', tamano_min=15, tamano_max=25)
        self.assertCountEqual(resultado, [self.tominejo_gigante])

    def test_combina_texto_y_filtro(self):
        resultado = buscar_especies('colibri', familia='Turdidae')
        self.assertCountEqual(resultado, [])

    def test_ordena_por_tamano_ascendente(self):
        resultado = list(buscar_especies('', ordenar='tamano_asc'))
        self.assertEqual(resultado, [self.colibri, self.tominejo_gigante, self.mirla])

    def test_especies_similares_misma_familia(self):
        similares = list(listar_especies_similares(self.colibri))
        self.assertEqual(similares, [self.tominejo_gigante])

    def test_especies_similares_excluye_a_si_misma(self):
        similares = listar_especies_similares(self.colibri)
        self.assertNotIn(self.colibri, similares)

    def test_sin_familia_no_hay_similares(self):
        especie_sin_familia = Especie.objects.create(
            nombre_cientifico='Especie sin familia', creado_por=self.revisor,
        )
        self.assertEqual(list(listar_especies_similares(especie_sin_familia)), [])

    def test_filtro_de_tamano_filtra_y_el_campo_queda_valido_para_recargar(self):
        # Bug real (25/08/2026): Django renderiza un float en español con
        # coma decimal ("15,0"), que un <input type="number"> no acepta —
        # el campo se veía vacío/roto al recargar la página con el filtro
        # puesto. El valor debe volver exactamente como se escribió.
        respuesta = self.client.get(reverse('catalogo:publico_listado'), {'tamano_min': '15', 'tamano_max': '25'})
        contenido = respuesta.content.decode()
        self.assertIn('Patagona gigas', contenido)
        self.assertNotIn('Colibri coruscans', contenido)
        self.assertNotIn('Turdus fuscater', contenido)
        self.assertIn('value="15"', contenido)
        self.assertIn('value="25"', contenido)
        self.assertNotIn('value="15,0"', contenido)
