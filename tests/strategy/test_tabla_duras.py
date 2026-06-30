"""
Tests para app.strategy.tabla_duras.

Los casos de esta suite estan tomados de la tabla de estrategia
basica estandar (mesas de 6-8 mazos, crupier se planta en soft 17).
Sirven como referencia fija: si alguien edita TABLA_DURAS por error,
estos tests deben detectarlo.
"""

import pytest

from app.strategy.reglas import Accion
from app.strategy.tabla_duras import obtener_accion_dura


class TestCasosClasicos:
    @pytest.mark.parametrize(
        "total,carta_crupier,accion_esperada",
        [
            (16, "10", Accion.RENDIRSE),  # 16 vs 10: rendirse
            (16, "9", Accion.RENDIRSE),  # 16 vs 9: rendirse tambien
            (16, "7", Accion.PEDIR),  # 16 vs 7: sin rendirse en esta columna, se pide
            (17, "A", Accion.PLANTARSE),
            (11, "6", Accion.DOBLAR),
            (10, "10", Accion.PEDIR),  # 10 vs 10 no se dobla (carta alta del crupier)
            (12, "4", Accion.PLANTARSE),
            (12, "2", Accion.PEDIR),  # 12 vs 2-3 se pide, no se planta
            (9, "3", Accion.DOBLAR),
            (9, "2", Accion.PEDIR),  # 9 vs 2 NO se dobla
        ],
    )
    def test_casos_de_referencia(self, total, carta_crupier, accion_esperada):
        assert obtener_accion_dura(total, carta_crupier) == accion_esperada


class TestRendirse:
    def test_quince_contra_as_es_rendirse(self):
        # Este caso documenta el bug encontrado y corregido durante el
        # desarrollo: la fila de 15 tenia "Pedir" en vez de "Rendirse"
        # contra el As. No debe volver a romperse.
        assert obtener_accion_dura(15, "A") == Accion.RENDIRSE

    def test_quince_contra_diez_es_rendirse(self):
        assert obtener_accion_dura(15, "10") == Accion.RENDIRSE

    def test_dieciseis_contra_diez_es_rendirse(self):
        assert obtener_accion_dura(16, "10") == Accion.RENDIRSE

    def test_dieciseis_contra_as_es_rendirse(self):
        assert obtener_accion_dura(16, "A") == Accion.RENDIRSE


class TestNormalizacionFiguras:
    @pytest.mark.parametrize("carta_crupier", ["10", "J", "Q", "K"])
    def test_figuras_se_tratan_igual_que_diez(self, carta_crupier):
        # 16 vs cualquier carta que valga 10 deberia dar el mismo resultado
        assert obtener_accion_dura(16, carta_crupier) == Accion.RENDIRSE


class TestRangosExtremos:
    @pytest.mark.parametrize("total", [5, 6, 7])
    def test_totales_bajos_siempre_piden(self, total):
        for carta_crupier in ["2", "7", "A"]:
            assert obtener_accion_dura(total, carta_crupier) == Accion.PEDIR

    @pytest.mark.parametrize("total", [18, 19, 20, 21])
    def test_totales_altos_siempre_se_plantan(self, total):
        for carta_crupier in ["2", "7", "A"]:
            assert obtener_accion_dura(total, carta_crupier) == Accion.PLANTARSE

    def test_total_menor_a_cinco_no_lanza_error(self):
        # Caso de seguridad: no deberia ocurrir en la practica, pero
        # no debe romper el programa.
        assert obtener_accion_dura(4, "5") == Accion.PEDIR

    def test_total_mayor_a_21_no_lanza_error(self):
        assert obtener_accion_dura(25, "5") == Accion.PLANTARSE
