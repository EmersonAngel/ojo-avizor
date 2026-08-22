"""Insignias por hitos (fuera del MVP original, pedido explícito del 22/08/2026)."""
from django.test import TestCase

from apps.cuentas import services


class EvaluarHitosTests(TestCase):
    def test_sin_aportes_ninguna_insignia_esta_conseguida(self):
        insignias = services.evaluar_hitos(aportes_aprobados=0, especies_distintas=0, racha=0)
        self.assertTrue(insignias)
        self.assertFalse(any(i['conseguida'] for i in insignias))

    def test_primer_aporte_se_consigue_con_un_solo_aporte_aprobado(self):
        insignias = services.evaluar_hitos(aportes_aprobados=1, especies_distintas=0, racha=0)
        por_clave = {i['clave']: i for i in insignias}
        self.assertTrue(por_clave['primer_aporte']['conseguida'])
        self.assertFalse(por_clave['diez_aportes']['conseguida'])

    def test_diez_aportes_tambien_cuenta_como_primer_aporte(self):
        insignias = services.evaluar_hitos(aportes_aprobados=10, especies_distintas=0, racha=0)
        por_clave = {i['clave']: i for i in insignias}
        self.assertTrue(por_clave['primer_aporte']['conseguida'])
        self.assertTrue(por_clave['diez_aportes']['conseguida'])
        self.assertFalse(por_clave['veinticinco_aportes']['conseguida'])

    def test_especies_distintas_activa_sus_propias_insignias(self):
        insignias = services.evaluar_hitos(aportes_aprobados=0, especies_distintas=5, racha=0)
        por_clave = {i['clave']: i for i in insignias}
        self.assertTrue(por_clave['primera_especie']['conseguida'])
        self.assertTrue(por_clave['cinco_especies']['conseguida'])
        self.assertFalse(por_clave['diez_especies']['conseguida'])

    def test_racha_activa_sus_propias_insignias(self):
        insignias = services.evaluar_hitos(aportes_aprobados=0, especies_distintas=0, racha=7)
        por_clave = {i['clave']: i for i in insignias}
        self.assertTrue(por_clave['racha_semana']['conseguida'])
        self.assertFalse(por_clave['racha_mes']['conseguida'])

    def test_faltan_calcula_lo_que_falta_para_la_siguiente(self):
        insignias = services.evaluar_hitos(aportes_aprobados=7, especies_distintas=0, racha=0)
        por_clave = {i['clave']: i for i in insignias}
        self.assertEqual(por_clave['diez_aportes']['faltan'], 3)
        self.assertEqual(por_clave['primer_aporte']['faltan'], 0)
