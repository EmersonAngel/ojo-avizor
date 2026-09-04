"""Registro de cuentas (RF-09, RF-27): el username técnico se deriva del
seudónimo, no se pide aparte (pedido explícito del 04/09/2026 — el
formulario original pedía ambos y no había forma de distinguirlos a simple
vista)."""
from django.test import TestCase

from apps.cuentas import services
from apps.cuentas.forms import RegistroForm
from apps.cuentas.models import Usuario


class RegistrarUsuarioTests(TestCase):
    def test_el_username_se_deriva_del_seudonimo(self):
        usuario = services.registrar_usuario(
            correo='andarrios@example.com',
            nombre_real='Ana Ríos',
            seudonimo='Andarríos',
            password='una-contraseña-larga-123',
        )
        # La tilde no se transcribe, se quita entera (limpieza vía regex de
        # caracteres válidos, igual que ya hacía adapters.py con Google).
        self.assertEqual(usuario.username, 'Andarros')

    def test_dos_seudonimos_que_limpian_igual_no_chocan_de_username(self):
        services.registrar_usuario(
            correo='primero@example.com',
            nombre_real='Primera Persona',
            seudonimo='Reinita!!',
            password='una-contraseña-larga-123',
        )
        segundo = services.registrar_usuario(
            correo='segundo@example.com',
            nombre_real='Segunda Persona',
            seudonimo='Reinita??',  # distinto seudónimo, mismo username limpio
            password='una-contraseña-larga-123',
        )
        self.assertEqual(segundo.username, 'Reinita2')

    def test_el_formulario_de_registro_ya_no_pide_username(self):
        self.assertNotIn('username', RegistroForm().fields)


class RegistrarVistaTests(TestCase):
    def test_registrarse_por_el_formulario_crea_la_cuenta_sin_pedir_username(self):
        respuesta = self.client.post('/es/cuentas/registrar/', {
            'correo': 'nuevo.observador@example.com',
            'nombre_real': 'Nuevo Observador',
            'seudonimo': 'AveNueva',
            'password1': 'una-contraseña-larga-123',
            'password2': 'una-contraseña-larga-123',
        })
        self.assertEqual(respuesta.status_code, 302)
        usuario = Usuario.objects.get(correo='nuevo.observador@example.com')
        self.assertEqual(usuario.seudonimo, 'AveNueva')
        self.assertTrue(usuario.username)
