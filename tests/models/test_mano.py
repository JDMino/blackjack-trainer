"""Tests para app.models.mano.Mano"""

import pytest

from app.models.carta import Carta
from app.models.mano import Mano


def carta(rango, palo="picas"):
    """Helper para crear cartas rapido en los tests, donde el palo no importa."""
    return Carta(rango, palo)


class TestManoVacia:
    def test_valor_de_mano_vacia_es_cero(self):
        assert Mano().valor == 0

    def test_agregar_carta_la_incluye_en_la_mano(self):
        mano = Mano()
        mano.agregar_carta(carta("7"))
        assert len(mano.cartas) == 1
        assert mano.cartas[0].rango == "7"


class TestValorManoDura:
    def test_dos_cartas_simples(self):
        mano = Mano([carta("10"), carta("6")])
        assert mano.valor == 16

    def test_tres_cartas(self):
        mano = Mano([carta("5"), carta("5"), carta("5")])
        assert mano.valor == 15

    def test_se_paso_de_21(self):
        mano = Mano([carta("K"), carta("Q"), carta("5")])
        assert mano.valor == 25
        assert mano.se_pasó is True


class TestReglaDelAs:
    def test_as_mas_seis_es_diecisiete_no_siete(self):
        mano = Mano([carta("A"), carta("6")])
        assert mano.valor == 17

    def test_as_se_baja_a_uno_si_se_pasaria_de_21(self):
        # As(11) + K(10) + 5 = 26 sin ajuste -> debe bajar el As a 1 -> 16
        mano = Mano([carta("A"), carta("K"), carta("5")])
        assert mano.valor == 16
        assert mano.se_pasó is False

    def test_dos_ases_mas_nueve_no_se_pasa(self):
        # 11+11+9=31 -> baja un As (21) -> ya no se pasa
        mano = Mano([carta("A"), carta("A"), carta("9")])
        assert mano.valor == 21
        assert mano.se_pasó is False

    def test_dos_ases_solos_valen_doce(self):
        # 11+11=22 -> baja un As -> 12
        mano = Mano([carta("A"), carta("A")])
        assert mano.valor == 12

    def test_tres_ases_mas_ocho_no_se_pasa(self):
        # 11+11+11+8=41 -> bajar Ases de uno en uno: 31, 21 -> resultado 21
        mano = Mano([carta("A"), carta("A"), carta("A"), carta("8")])
        assert mano.valor == 21


class TestEsBlanda:
    def test_as_mas_seis_es_blanda(self):
        mano = Mano([carta("A"), carta("6")])
        assert mano.es_blanda is True

    def test_as_que_se_cuenta_como_uno_no_es_blanda(self):
        # As+K+5=16 (el As ya vale 1 obligatoriamente) -> mano dura
        mano = Mano([carta("A"), carta("K"), carta("5")])
        assert mano.es_blanda is False

    def test_mano_sin_as_no_es_blanda(self):
        mano = Mano([carta("10"), carta("6")])
        assert mano.es_blanda is False


class TestEsPar:
    def test_dos_cartas_mismo_rango_es_par(self):
        mano = Mano([carta("8"), carta("8")])
        assert mano.es_par is True

    def test_dos_cartas_distinto_rango_no_es_par(self):
        mano = Mano([carta("8"), carta("9")])
        assert mano.es_par is False

    def test_tres_cartas_mismo_rango_no_cuenta_como_par(self):
        # es_par solo aplica a la mano inicial de 2 cartas
        mano = Mano([carta("8"), carta("8"), carta("8")])
        assert mano.es_par is False

    def test_una_sola_carta_no_es_par(self):
        mano = Mano([carta("8")])
        assert mano.es_par is False


class TestEsBlackjack:
    def test_as_mas_figura_es_blackjack(self):
        mano = Mano([carta("A"), carta("K")])
        assert mano.es_blackjack is True

    def test_veintiuno_con_tres_cartas_no_es_blackjack(self):
        # un 21 con mas de 2 cartas no cuenta como blackjack natural
        mano = Mano([carta("7"), carta("7"), carta("7")])
        assert mano.valor == 21
        assert mano.es_blackjack is False

    def test_veinte_no_es_blackjack(self):
        mano = Mano([carta("10"), carta("K")])
        assert mano.es_blackjack is False


class TestRepr:
    def test_repr_incluye_cartas_y_valor(self):
        mano = Mano([carta("10"), carta("6")])
        texto = repr(mano)
        assert "10 de picas" in texto
        assert "16" in texto
