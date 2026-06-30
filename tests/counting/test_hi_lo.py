"""Tests para app.counting.hi_lo.ContadorHiLo"""

import pytest

from app.models.carta import Carta
from app.counting.hi_lo import ContadorHiLo


def carta(rango):
    return Carta(rango, "picas")


class TestConstruccion:
    def test_num_mazos_por_defecto_es_seis(self):
        contador = ContadorHiLo()
        assert contador.num_mazos == 6

    def test_num_mazos_cero_o_negativo_lanza_error(self):
        with pytest.raises(ValueError):
            ContadorHiLo(num_mazos=0)
        with pytest.raises(ValueError):
            ContadorHiLo(num_mazos=-1)

    def test_estado_inicial_en_cero(self):
        contador = ContadorHiLo(num_mazos=6)
        assert contador.running_count == 0
        assert contador.cartas_vistas == 0


class TestValorPorRango:
    @pytest.mark.parametrize("rango", ["2", "3", "4", "5", "6"])
    def test_cartas_bajas_suman_mas_uno(self, rango):
        contador = ContadorHiLo()
        contador.registrar_carta(carta(rango))
        assert contador.running_count == 1

    @pytest.mark.parametrize("rango", ["7", "8", "9"])
    def test_cartas_neutras_no_cambian_el_conteo(self, rango):
        contador = ContadorHiLo()
        contador.registrar_carta(carta(rango))
        assert contador.running_count == 0

    @pytest.mark.parametrize("rango", ["10", "J", "Q", "K", "A"])
    def test_cartas_altas_restan_uno(self, rango):
        contador = ContadorHiLo()
        contador.registrar_carta(carta(rango))
        assert contador.running_count == -1


class TestRunningCountAcumulado:
    def test_secuencia_de_varias_cartas(self):
        contador = ContadorHiLo()
        for rango in ["5", "6", "10"]:  # +1 +1 -1
            contador.registrar_carta(carta(rango))
        assert contador.running_count == 1

    def test_cartas_vistas_se_incrementa_por_cada_carta(self):
        contador = ContadorHiLo()
        for rango in ["5", "6", "10", "7"]:
            contador.registrar_carta(carta(rango))
        assert contador.cartas_vistas == 4


class TestMazosRestantesYTrueCount:
    def test_mazos_restantes_al_inicio_es_num_mazos(self):
        contador = ContadorHiLo(num_mazos=6)
        assert contador.mazos_restantes == pytest.approx(6.0)

    def test_mazos_restantes_disminuye_con_cartas_vistas(self):
        contador = ContadorHiLo(num_mazos=1)
        for _ in range(26):  # medio mazo visto
            contador.registrar_carta(carta("7"))  # neutra, no afecta el running count
        assert contador.mazos_restantes == pytest.approx(0.5)

    def test_mazos_restantes_tiene_piso_de_0_5(self):
        # Si vemos casi todo el mazo, no debe bajar de 0.5 (evita division por casi cero)
        contador = ContadorHiLo(num_mazos=1)
        for _ in range(52):
            contador.registrar_carta(carta("7"))
        assert contador.mazos_restantes == pytest.approx(0.5)

    def test_true_count_es_running_count_sobre_mazos_restantes(self):
        contador = ContadorHiLo(num_mazos=2)
        for rango in ["5", "6", "5", "6"]:  # running count = +4
            contador.registrar_carta(carta(rango))
        # mazos_restantes = (104 - 4) / 52 = ~1.923
        true_count_esperado = 4 / contador.mazos_restantes
        assert contador.true_count == pytest.approx(true_count_esperado)

    def test_true_count_cero_cuando_running_count_es_cero(self):
        contador = ContadorHiLo(num_mazos=6)
        contador.registrar_carta(carta("7"))  # neutra
        assert contador.true_count == pytest.approx(0.0)


class TestReiniciar:
    def test_reiniciar_pone_todo_en_cero(self):
        contador = ContadorHiLo(num_mazos=6)
        contador.registrar_carta(carta("5"))
        contador.registrar_carta(carta("10"))
        contador.reiniciar()
        assert contador.running_count == 0
        assert contador.cartas_vistas == 0

    def test_reiniciar_no_cambia_num_mazos(self):
        contador = ContadorHiLo(num_mazos=8)
        contador.registrar_carta(carta("5"))
        contador.reiniciar()
        assert contador.num_mazos == 8


class TestRepr:
    def test_repr_no_lanza_error_y_contiene_datos_clave(self):
        contador = ContadorHiLo(num_mazos=6)
        contador.registrar_carta(carta("5"))
        texto = repr(contador)
        assert "running_count" in texto
        assert "true_count" in texto
