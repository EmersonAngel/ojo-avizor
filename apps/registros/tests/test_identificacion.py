"""Ayuda de la comunidad para identificar un registro (RF-19, RF-29)."""
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.cuentas.models import Usuario
from apps.registros import services
from apps.registros.models import ComentarioIdentificacion, VotoComentario


class VotarComentarioTests(TestCase):
    def setUp(self):
        self.observador = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )
        self.revisor = Usuario.objects.create_user(
            username='rev1', correo='rev1@example.com', nombre_real='Revisor de Prueba',
            seudonimo='seudo-revisor', password='clave-segura-123', rol=Usuario.Rol.REVISOR,
        )
        self.registro = services.crear_registro(
            usuario=self.observador, especie=None, lugar='Vereda X',
            fecha_avistamiento=date.today(), sin_identificar=True,
            comportamiento='Se posaba en una rama baja cerca del agua.',
        )
        self.comentario = services.crear_comentario_identificacion(
            registro=self.registro, usuario=self.observador, texto='¿Será un azulejo?',
        )

    def test_primer_voto_se_crea(self):
        services.votar_comentario(comentario=self.comentario, usuario=self.revisor, valor=VotoComentario.Valor.ME_GUSTA)
        self.assertEqual(self.comentario.total_me_gusta, 1)
        self.assertEqual(self.comentario.total_no_me_gusta, 0)

    def test_repetir_el_mismo_voto_lo_retira(self):
        services.votar_comentario(comentario=self.comentario, usuario=self.revisor, valor=VotoComentario.Valor.ME_GUSTA)
        services.votar_comentario(comentario=self.comentario, usuario=self.revisor, valor=VotoComentario.Valor.ME_GUSTA)
        self.assertEqual(VotoComentario.objects.filter(comentario=self.comentario).count(), 0)

    def test_votar_lo_contrario_cambia_el_voto_en_vez_de_sumar_otro(self):
        services.votar_comentario(comentario=self.comentario, usuario=self.revisor, valor=VotoComentario.Valor.ME_GUSTA)
        services.votar_comentario(comentario=self.comentario, usuario=self.revisor, valor=VotoComentario.Valor.NO_ME_GUSTA)
        self.assertEqual(VotoComentario.objects.filter(comentario=self.comentario).count(), 1)
        self.assertEqual(self.comentario.total_me_gusta, 0)
        self.assertEqual(self.comentario.total_no_me_gusta, 1)

    def test_comentario_vacio_es_invalido(self):
        with self.assertRaises(ValueError):
            services.crear_comentario_identificacion(registro=self.registro, usuario=self.observador, texto='   ')


class VistaVotarComentarioTests(TestCase):
    def setUp(self):
        self.observador = Usuario.objects.create_user(
            username='obs1', correo='obs1@example.com', nombre_real='Observador de Prueba',
            seudonimo='seudo1', password='clave-segura-123',
        )
        self.registro = services.crear_registro(
            usuario=self.observador, especie=None, lugar='Vereda X',
            fecha_avistamiento=date.today(), sin_identificar=True,
            comportamiento='Se posaba en una rama baja cerca del agua.',
        )
        self.comentario = services.crear_comentario_identificacion(
            registro=self.registro, usuario=self.observador, texto='¿Será un azulejo?',
        )

    def test_un_observador_no_puede_votar(self):
        self.client.force_login(self.observador)
        respuesta = self.client.post(
            reverse('registros:identificar_votar_comentario', args=[self.comentario.pk]),
            {'valor': VotoComentario.Valor.ME_GUSTA},
        )
        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(VotoComentario.objects.count(), 0)

    def test_la_vista_publica_no_expone_coordenadas(self):
        self.registro.latitud = 4.336
        self.registro.longitud = -75.699
        self.registro.save(update_fields=['latitud', 'longitud'])

        self.client.force_login(self.observador)
        respuesta = self.client.get(reverse('registros:identificar_detalle', args=[self.registro.pk]))
        contenido = respuesta.content.decode()
        self.assertNotIn('4.336', contenido)
        self.assertNotIn('-75.699', contenido)
