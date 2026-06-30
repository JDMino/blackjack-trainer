"""Tests para app.game.partida.Partida"""

import pytest

from app.models.carta import Carta
from app.game.partida import Partida
from app.strategy.reglas import Accion, ReglasMesa


def carta(rango):
    return Carta(rango, "picas")


class TestObservacionDeCartas:
    def test_observar_carta_jugador_la_agrega_a_la_mano(self):
        partida = Partida()
        partida.observar_carta_jugador(carta("10"))
        partida.observar_carta_jugador(carta("6"))
        assert partida.mano_jugador.valor == 16

    def test_observar_carta_crupier_la_agrega_a_su_mano(self):
        partida = Partida()
        partida.observar_carta_crupier(carta("A"))
        assert partida.mano_crupier.valor == 11

    def test_cada_carta_observada_se_cuenta_en_hi_lo(self):
        partida = Partida()
        partida.observar_carta_jugador(carta("5"))  # +1
        partida.observar_carta_crupier(carta("10"))  # -1
        assert partida.contador.running_count == 0


class TestRecomendacionActual:
    def test_sin_cartas_devuelve_none(self):
        partida = Partida()
        assert partida.recomendacion_actual() is None

    def test_sin_carta_de_crupier_devuelve_none(self):
        partida = Partida()
        partida.observar_carta_jugador(carta("10"))
        assert partida.recomendacion_actual() is None

    def test_sin_carta_de_jugador_devuelve_none(self):
        partida = Partida()
        partida.observar_carta_crupier(carta("10"))
        assert partida.recomendacion_actual() is None

    def test_con_ambas_manos_devuelve_accion_correcta(self):
        partida = Partida()
        partida.observar_carta_jugador(carta("10"))
        partida.observar_carta_jugador(carta("6"))
        partida.observar_carta_crupier(carta("10"))
        assert partida.recomendacion_actual() == Accion.PEDIR


class TestNuevaMano:
    def test_nueva_mano_limpia_las_manos(self):
        partida = Partida()
        partida.observar_carta_jugador(carta("10"))
        partida.observar_carta_crupier(carta("6"))
        partida.nueva_mano()
        assert partida.mano_jugador.valor == 0
        assert partida.mano_crupier.valor == 0

    def test_nueva_mano_mantiene_el_running_count(self):
        partida = Partida()
        partida.observar_carta_jugador(carta("5"))  # +1
        partida.nueva_mano()
        assert partida.contador.running_count == 1


class TestNuevoZapato:
    def test_nuevo_zapato_reinicia_el_running_count(self):
        partida = Partida()
        partida.observar_carta_jugador(carta("5"))  # +1
        partida.nuevo_zapato()
        assert partida.contador.running_count == 0

    def test_nuevo_zapato_tambien_limpia_las_manos(self):
        partida = Partida()
        partida.observar_carta_jugador(carta("10"))
        partida.nuevo_zapato()
        assert partida.mano_jugador.valor == 0


class TestReglasPersonalizadas:
    def test_partida_usa_num_mazos_de_reglas_mesa(self):
        partida = Partida(reglas=ReglasMesa(num_mazos=2))
        assert partida.contador.num_mazos == 2

    def test_partida_sin_reglas_usa_default_de_seis_mazos(self):
        partida = Partida()
        assert partida.contador.num_mazos == 6


class TestSecuenciaCompleta:
    def test_dos_manos_consecutivas_en_el_mismo_zapato(self):
        partida = Partida()

        # Mano 1
        partida.observar_carta_jugador(carta("10"))
        partida.observar_carta_jugador(carta("6"))
        partida.observar_carta_crupier(carta("10"))
        assert partida.recomendacion_actual() == Accion.PEDIR

        # Nueva mano, mismo zapato
        partida.nueva_mano()
        partida.observar_carta_jugador(carta("A"))
        partida.observar_carta_jugador(carta("7"))
        partida.observar_carta_crupier(carta("6"))
        assert partida.recomendacion_actual() == Accion.DOBLAR

        # El running count acumulo ambas manos: (-1) + (0 -1 +1) = -1
        assert partida.contador.running_count == -1
