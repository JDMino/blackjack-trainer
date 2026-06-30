"""Tests para app.overlay.estado.EstadoOverlay"""

from app.models.carta import Carta
from app.game.partida import Partida
from app.overlay.estado import EstadoOverlay
from app.strategy.reglas import Accion


class TestFormatoDeTextos:
    def test_running_count_positivo_muestra_signo_mas(self):
        estado = EstadoOverlay(running_count=6)
        assert estado.texto_running_count == "+6"

    def test_running_count_negativo_muestra_signo_menos(self):
        estado = EstadoOverlay(running_count=-3)
        assert estado.texto_running_count == "-3"

    def test_true_count_se_formatea_con_un_decimal(self):
        estado = EstadoOverlay(true_count=2.34)
        assert estado.texto_true_count == "+2.3"

    def test_mano_jugador_en_cero_muestra_guion(self):
        estado = EstadoOverlay(valor_mano_jugador=0)
        assert estado.texto_mano_jugador == "—"

    def test_mano_jugador_con_valor_lo_muestra(self):
        estado = EstadoOverlay(valor_mano_jugador=16)
        assert estado.texto_mano_jugador == "16"

    def test_carta_crupier_ausente_muestra_guion(self):
        estado = EstadoOverlay(rango_carta_crupier=None)
        assert estado.texto_carta_crupier == "—"

    def test_carta_crupier_presente_la_muestra(self):
        estado = EstadoOverlay(rango_carta_crupier="10")
        assert estado.texto_carta_crupier == "10"

    def test_recomendacion_ausente_muestra_guion(self):
        estado = EstadoOverlay(recomendacion=None)
        assert estado.texto_recomendacion == "—"

    def test_recomendacion_presente_muestra_su_valor(self):
        estado = EstadoOverlay(recomendacion=Accion.PEDIR)
        assert estado.texto_recomendacion == "Pedir"


class TestDesdePartida:
    def test_estado_vacio_desde_partida_sin_cartas(self):
        partida = Partida()
        estado = EstadoOverlay.desde_partida(partida)
        assert estado.valor_mano_jugador == 0
        assert estado.rango_carta_crupier is None
        assert estado.recomendacion is None

    def test_estado_completo_desde_partida_con_cartas(self):
        partida = Partida()
        partida.observar_carta_jugador(Carta("10", "picas"))
        partida.observar_carta_jugador(Carta("6", "picas"))
        partida.observar_carta_crupier(Carta("10", "picas"))

        estado = EstadoOverlay.desde_partida(partida)

        assert estado.valor_mano_jugador == 16
        assert estado.rango_carta_crupier == "10"
        assert estado.recomendacion == Accion.PEDIR
        assert estado.running_count == partida.contador.running_count
        assert estado.true_count == partida.contador.true_count
