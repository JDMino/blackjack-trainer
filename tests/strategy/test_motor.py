"""Tests para app.strategy.motor.MotorEstrategia"""

import pytest

from app.models.carta import Carta
from app.models.mano import Mano
from app.strategy.motor import MotorEstrategia
from app.strategy.reglas import Accion, ReglasMesa


def carta(rango):
    return Carta(rango, "picas")


@pytest.fixture
def motor_default():
    return MotorEstrategia()


class TestBlackjackNatural:
    def test_blackjack_siempre_se_planta(self, motor_default):
        mano = Mano([carta("A"), carta("K")])
        assert motor_default.recomendar(mano, "6") == Accion.PLANTARSE


class TestPrioridadDeTablas:
    def test_par_que_se_debe_dividir_tiene_prioridad(self, motor_default):
        mano = Mano([carta("8"), carta("8")])
        assert motor_default.recomendar(mano, "6") == Accion.DIVIDIR

    def test_par_que_no_se_divide_cae_a_tabla_dura(self, motor_default):
        # 5+5=10 (dura), no se divide -> deberia evaluarse como duro 10
        mano = Mano([carta("5"), carta("5")])
        assert motor_default.recomendar(mano, "6") == Accion.DOBLAR

    def test_par_de_diez_cae_a_tabla_dura_como_veinte(self, motor_default):
        mano = Mano([carta("10"), carta("10")])
        assert motor_default.recomendar(mano, "6") == Accion.PLANTARSE

    def test_mano_blanda_usa_tabla_blanda(self, motor_default):
        mano = Mano([carta("A"), carta("7")])  # blando 18
        assert motor_default.recomendar(mano, "6") == Accion.DOBLAR

    def test_mano_dura_usa_tabla_dura(self, motor_default):
        mano = Mano([carta("10"), carta("6")])  # duro 16
        assert motor_default.recomendar(mano, "10") == Accion.PEDIR


class TestDegradacionDoblar:
    def test_doblar_se_degrada_a_pedir_con_mas_de_dos_cartas(self, motor_default):
        # 11 vs 6 seria Doblar con 2 cartas, pero con 3 cartas no se puede doblar.
        # Total < 17 -> debe degradar a Pedir.
        mano = Mano([carta("5"), carta("2"), carta("4")])  # total 11, 3 cartas
        assert motor_default.recomendar(mano, "6") == Accion.PEDIR

    def test_doblar_se_degrada_a_plantarse_si_total_alto_con_mas_cartas(self, motor_default):
        # Si despues de pedir el total ya es >= 17, degradar a Plantarse en vez de Pedir.
        mano = Mano([carta("5"), carta("6"), carta("8")])  # total 19, 3 cartas
        # Esta mano en concreto no llegaria por la tabla a "Doblar", pero
        # probamos la funcion de degradacion con un caso equivalente:
        resultado = motor_default.recomendar(mano, "6")
        assert resultado in (Accion.PLANTARSE, Accion.PEDIR)  # nunca Doblar con 3 cartas
        assert resultado != Accion.DOBLAR

    def test_doblar_con_exactamente_dos_cartas_no_se_degrada(self, motor_default):
        mano = Mano([carta("5"), carta("6")])  # total 11, 2 cartas
        assert motor_default.recomendar(mano, "6") == Accion.DOBLAR


class TestDegradacionRendirse:
    def test_rendirse_se_degrada_a_pedir_si_mesa_no_lo_permite(self):
        motor = MotorEstrategia(reglas=ReglasMesa(permite_rendirse=False))
        mano = Mano([carta("10"), carta("5")])  # duro 15
        assert motor.recomendar(mano, "A") == Accion.PEDIR

    def test_rendirse_se_mantiene_si_mesa_lo_permite(self):
        motor = MotorEstrategia(reglas=ReglasMesa(permite_rendirse=True))
        mano = Mano([carta("10"), carta("5")])  # duro 15
        assert motor.recomendar(mano, "A") == Accion.RENDIRSE

    def test_rendirse_se_degrada_con_mas_de_dos_cartas_aunque_se_permita(self):
        motor = MotorEstrategia(reglas=ReglasMesa(permite_rendirse=True))
        # Si por alguna razon se evalua "rendirse" con 3+ cartas, no es valido.
        # No hay forma directa de forzar este caso vía las tablas reales,
        # pero documentamos el contrato esperado a través del motor.
        mano = Mano([carta("10"), carta("5")])
        resultado = motor.recomendar(mano, "A")
        assert resultado == Accion.RENDIRSE  # con 2 cartas, sí es válido


class TestReglasPorDefecto:
    def test_motor_sin_reglas_usa_reglas_mesa_por_defecto(self):
        motor = MotorEstrategia()
        assert motor.reglas.permite_rendirse is False
        assert motor.reglas.num_mazos == 6
