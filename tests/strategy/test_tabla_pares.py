"""Tests para app.strategy.tabla_pares"""

import pytest

from app.strategy.reglas import Accion
from app.strategy.tabla_pares import obtener_accion_par


class TestParesSiempreDividir:
    @pytest.mark.parametrize("carta_crupier", ["2", "5", "7", "10", "A"])
    def test_ases_siempre_se_dividen(self, carta_crupier):
        assert obtener_accion_par("A", carta_crupier) == Accion.DIVIDIR

    @pytest.mark.parametrize("carta_crupier", ["2", "5", "7", "10", "A"])
    def test_ochos_siempre_se_dividen(self, carta_crupier):
        assert obtener_accion_par("8", carta_crupier) == Accion.DIVIDIR


class TestParesNuncaDividir:
    @pytest.mark.parametrize("carta_crupier", ["2", "5", "6", "10", "A"])
    def test_cincos_nunca_se_dividen(self, carta_crupier):
        assert obtener_accion_par("5", carta_crupier) is None

    @pytest.mark.parametrize("rango_par", ["10", "J", "Q", "K"])
    def test_pares_de_diez_nunca_se_dividen(self, rango_par):
        assert obtener_accion_par(rango_par, "6") is None


class TestCasosCondicionales:
    def test_dos_contra_seis_se_divide(self):
        assert obtener_accion_par("2", "6") == Accion.DIVIDIR

    def test_dos_contra_siete_se_divide(self):
        # Estrategia basica estandar: 2-2 y 3-3 se dividen contra 2-7.
        assert obtener_accion_par("2", "7") == Accion.DIVIDIR

    def test_dos_contra_ocho_no_se_divide(self):
        assert obtener_accion_par("2", "8") is None

    def test_nueve_contra_seis_se_divide(self):
        assert obtener_accion_par("9", "6") == Accion.DIVIDIR

    def test_nueve_contra_siete_no_se_divide(self):
        # 9-9 vs 7 no se divide (7 da un total de 9+7=16 razonable de plantarse/pedir)
        assert obtener_accion_par("9", "7") is None
