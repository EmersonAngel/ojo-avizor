"""Buscador de especie tipo eBird y cantidad de individuos obligatoria en el
formulario web (fuera del MVP original, pedido explícito del 30/08/2026)."""
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.catalogo.models import Especie, NombreComun
from apps.cuentas.models import Usuario


class EspecieAutocompletarTests(TestCase):
    def setUp(self):
        self.revisor = Usuario.objects.create_user(
            username='rev1', correo='rev1@example.com', nombre_real='Revisora de Prueba',
            seudonimo='revisora1', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
        )
        self.colibri = Especie.objects.create(nombre_cientifico='Colibri coruscans', creado_por=self.revisor)
        NombreComun.objects.create(especie=self.colibri, nombre='Colibrí chillón')
        self.gallinazo = Especie.objects.create(nombre_cientifico='Coragyps atratus', creado_por=self.revisor)

    def test_es_publico_no_requiere_sesion(self):
        respuesta = self.client.get(reverse('registros:especie_autocompletar'), {'q': 'colib'})
        self.assertEqual(respuesta.status_code, 200)

    def test_busca_por_nombre_cientifico(self):
        respuesta = self.client.get(reverse('registros:especie_autocompletar'), {'q': 'coragyps'})
        self.assertContains(respuesta, 'Coragyps atratus')
        self.assertNotContains(respuesta, 'Colibri coruscans')

    def test_busca_por_nombre_comun(self):
        respuesta = self.client.get(reverse('registros:especie_autocompletar'), {'q': 'chillón'})
        self.assertContains(respuesta, 'Colibri coruscans')

    def test_sin_texto_no_devuelve_nada(self):
        respuesta = self.client.get(reverse('registros:especie_autocompletar'))
        self.assertNotContains(respuesta, 'Colibri coruscans')
        self.assertNotContains(respuesta, 'Coragyps atratus')

    def test_sin_resultados_avisa(self):
        respuesta = self.client.get(reverse('registros:especie_autocompletar'), {'q': 'zzz-inexistente'})
        self.assertContains(respuesta, 'No encontramos')


class CantidadIndividuosFormularioTests(TestCase):
    def setUp(self):
        self.observador = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )
        self.client.force_login(self.observador)

    def _datos_minimos(self, **overrides):
        datos = {
            'lugar': 'Vereda X', 'fecha_avistamiento': date.today().isoformat(),
            'departamento': 'Quindío', 'municipio': 'Pijao', 'cantidad_individuos': '1',
        }
        datos.update(overrides)
        return datos

    def test_sin_cantidad_individuos_el_formulario_es_invalido(self):
        datos = self._datos_minimos()
        del datos['cantidad_individuos']
        respuesta = self.client.post(reverse('registros:crear'), datos)
        self.assertEqual(respuesta.status_code, 200)  # vuelve a mostrar el formulario, no redirige
        self.assertFormError(respuesta.context['form'], 'cantidad_individuos', 'Este campo es obligatorio.')

    def test_con_cantidad_individuos_el_registro_se_crea(self):
        respuesta = self.client.post(reverse('registros:crear'), self._datos_minimos(cantidad_individuos='3'))
        self.assertRedirects(respuesta, reverse('registros:enviado'))
        from apps.registros.models import Registro
        registro = Registro.objects.get()
        self.assertEqual(registro.cantidad_individuos, 3)


class CodigoReproductivoFormularioTests(TestCase):
    """Se clasifica aparte, no se mezcla con el texto de comportamiento
    (pedido explícito del 31/08/2026); y es un solo valor, no varios (pedido
    explícito del 01/09/2026): la guía oficial de eBird pide elegir el de
    mayor jerarquía observado, nunca combinar códigos."""

    def setUp(self):
        self.observador = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )
        self.client.force_login(self.observador)

    def _datos_minimos(self, **overrides):
        datos = {
            'lugar': 'Vereda X', 'fecha_avistamiento': date.today().isoformat(),
            'departamento': 'Quindío', 'municipio': 'Pijao', 'cantidad_individuos': '1',
        }
        datos.update(overrides)
        return datos

    def test_codigo_elegido_queda_en_su_propio_campo(self):
        respuesta = self.client.post(
            reverse('registros:crear'),
            self._datos_minimos(codigo_reproductivo='NY', comportamiento='Posado en una rama.'),
        )
        self.assertRedirects(respuesta, reverse('registros:enviado'))
        from apps.registros.models import Registro
        registro = Registro.objects.get()
        self.assertEqual(registro.codigo_reproductivo, 'NY')
        self.assertEqual(registro.comportamiento, 'Posado en una rama.')
        self.assertNotIn('NY', registro.comportamiento)

    def test_codigo_no_reconocido_es_invalido(self):
        respuesta = self.client.post(
            reverse('registros:crear'), self._datos_minimos(codigo_reproductivo='ZZ'),
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].has_error('codigo_reproductivo'))

    def test_sin_codigo_es_valido(self):
        respuesta = self.client.post(reverse('registros:crear'), self._datos_minimos())
        self.assertRedirects(respuesta, reverse('registros:enviado'))
