"""El token de la app móvil se guarda como hash, no en texto plano
(hallazgo de la revisión de seguridad del 25/08/2026)."""
from django.test import TestCase

from apps.api_movil.models import TokenAcceso
from apps.cuentas.models import Usuario


class TokenHashTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )

    def test_crear_no_guarda_el_token_en_claro(self):
        _, token_en_claro = TokenAcceso.crear(self.usuario)
        fila = TokenAcceso.objects.get(usuario=self.usuario)
        self.assertNotEqual(fila.token_hash, token_en_claro)
        self.assertNotIn(token_en_claro, fila.token_hash)

    def test_obtener_por_token_encuentra_el_token_correcto(self):
        instancia, token_en_claro = TokenAcceso.crear(self.usuario)
        encontrado = TokenAcceso.obtener_por_token(token_en_claro)
        self.assertEqual(encontrado.pk, instancia.pk)

    def test_token_incorrecto_no_encuentra_nada(self):
        TokenAcceso.crear(self.usuario)
        with self.assertRaises(TokenAcceso.DoesNotExist):
            TokenAcceso.obtener_por_token('token-que-no-existe')
