"""Tag {% estatico_v %} (fuera del MVP original, pedido explícito del
31/08/2026 tras encontrar que el navegador podía reusar CSS/JS viejo: sin
versión en la URL, una recarga normal no siempre vuelve a pedir el
archivo)."""
from django.test import SimpleTestCase

from apps.catalogo.templatetags.estaticos import estatico_v


class EstaticoVTests(SimpleTestCase):
    def test_archivo_existente_lleva_version(self):
        url = estatico_v('css/entrada.css')
        self.assertRegex(url, r'^/static/css/entrada\.css\?v=\d+$')

    def test_archivo_inexistente_no_rompe(self):
        # Se degrada al comportamiento normal de {% static %}, sin versión.
        url = estatico_v('css/no-existe-de-verdad.css')
        self.assertEqual(url, '/static/css/no-existe-de-verdad.css')
