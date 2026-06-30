"""Tests para app.strategy.tabla_blandas"""

import pytest

from app.strategy.reglas import Accion
from app.strategy.tabla_blandas import obtener_accion_blanda


class TestCasosClasicos:
    @pytest.mark.parametrize(
        "total,carta_crupier,accion_esperada",
        [
            (18, "9", Accion.PEDIR),     # A+7 vs 9
            (18, "6", Accion.DOBLAR),    # A+7 vs 6
            (18, "2", Accion.PLANTARSE),  # A+7 vs 2
            (17, "6", Accion.DOBLAR),    # A+6 vs 6
            (13, "5", Accion.DOBLAR),    # A+2 vs 5
            (13, "7", Accion.PEDIR),     # A+2 vs 7
            (19, "6", Accion.PLANTARSE),  # A+8 siempre se planta
            (20, "6", Accion.PLANTARSE),  # A+9 siempre se planta
        ],
    )
    def test_casos_de_referencia(self, total, carta_crupier, accion_esperada):
        assert obtener_accion_blanda(total, carta_crupier) == accion_esperada


class TestRangosExtremos:
    def test_blackjack_no_lanza_error(self):
        # A+10=21 se gestiona aparte (MotorEstrategia), pero esta
        # funcion no debe romperse si se le pasa 21 por error.
        assert obtener_accion_blanda(21, "6") == Accion.PLANTARSE

    def test_total_invalido_bajo_no_lanza_error(self):
        assert obtener_accion_blanda(10, "6") == Accion.PEDIR
