"""Tests para app.models.carta.Carta"""

import pytest

from app.models.carta import Carta, PALOS_VALIDOS, RANGOS_VALIDOS


class TestConstruccion:
    def test_construccion_valida(self):
        carta = Carta("7", "corazones")
        assert carta.rango == "7"
        assert carta.palo == "corazones"

    def test_rango_invalido_lanza_error(self):
        with pytest.raises(ValueError):
            Carta("11", "corazones")

    def test_palo_invalido_lanza_error(self):
        with pytest.raises(ValueError):
            Carta("7", "estrellas")

    @pytest.mark.parametrize("rango", RANGOS_VALIDOS)
    def test_todos_los_rangos_validos_se_aceptan(self, rango):
        carta = Carta(rango, "picas")
        assert carta.rango == rango

    @pytest.mark.parametrize("palo", PALOS_VALIDOS)
    def test_todos_los_palos_validos_se_aceptan(self, palo):
        carta = Carta("7", palo)
        assert carta.palo == palo


class TestValor:
    @pytest.mark.parametrize(
        "rango,valor_esperado",
        [
            ("2", 2), ("3", 3), ("4", 4), ("5", 5), ("6", 6),
            ("7", 7), ("8", 8), ("9", 9), ("10", 10),
            ("J", 10), ("Q", 10), ("K", 10),
            ("A", 11),  # valor "alto" por defecto; Mano decide si baja a 1
        ],
    )
    def test_valor_de_cada_rango(self, rango, valor_esperado):
        assert Carta(rango, "picas").valor == valor_esperado


class TestPropiedades:
    def test_es_as_true_para_as(self):
        assert Carta("A", "picas").es_as is True

    def test_es_as_false_para_otro_rango(self):
        assert Carta("K", "picas").es_as is False

    @pytest.mark.parametrize("rango", ["10", "J", "Q", "K"])
    def test_es_figura_o_diez_true(self, rango):
        assert Carta(rango, "picas").es_figura_o_diez is True

    @pytest.mark.parametrize("rango", ["2", "9", "A"])
    def test_es_figura_o_diez_false(self, rango):
        assert Carta(rango, "picas").es_figura_o_diez is False


class TestComparacionYRepresentacion:
    def test_igualdad_mismo_rango_y_palo(self):
        assert Carta("7", "picas") == Carta("7", "picas")

    def test_desigualdad_distinto_rango(self):
        assert Carta("7", "picas") != Carta("8", "picas")

    def test_desigualdad_distinto_palo(self):
        assert Carta("7", "picas") != Carta("7", "corazones")

    def test_comparacion_con_otro_tipo_no_falla(self):
        # __eq__ debe devolver NotImplemented (no lanzar excepcion) ante tipos distintos.
        assert (Carta("7", "picas") == "7 de picas") is False

    def test_str_legible(self):
        assert str(Carta("A", "corazones")) == "A de corazones"

    def test_repr_para_depuracion(self):
        assert repr(Carta("A", "corazones")) == "Carta('A', 'corazones')"
