"""
Tests para app.game.bucle_aplicacion.BucleAplicacion.

El foco principal de esta suite es la DEDUPLICACION: verificar que
una misma carta fisica, vista en multiples frames consecutivos, se
registra una sola vez en Partida (y por lo tanto en el conteo Hi-Lo).
"""

import numpy as np
import pytest

from app.game.bucle_aplicacion import BucleAplicacion
from app.game.partida import Partida
from app.recognition.resultado import ResultadoReconocimiento
from app.strategy.reglas import ReglasMesa
from app.vision.region_candidata import RegionCandidata


def region_falsa(x):
    return RegionCandidata(x=x, y=0, ancho=40, alto=60, imagen=np.zeros((60, 40, 3), dtype=np.uint8))


@pytest.fixture
def partida():
    return Partida(reglas=ReglasMesa(num_mazos=6))


@pytest.fixture
def mocks(mocker):
    """Provee mocks de capturador, procesador y reconocedor, listos para configurar por test."""
    capturador = mocker.MagicMock()
    capturador.capturar_frame.return_value = np.zeros((10, 10, 4), dtype=np.uint8)
    procesador = mocker.MagicMock()
    reconocedor = mocker.MagicMock()
    return capturador, procesador, reconocedor


class TestRegistroDeCartaNueva:
    def test_una_carta_nueva_se_registra_en_partida(self, mocks, partida):
        capturador, procesador, reconocedor = mocks
        procesador.detectar_regiones_candidatas.return_value = [region_falsa(0)]
        reconocedor.reconocer.return_value = ResultadoReconocimiento(rango="10", confianza=0.95)

        bucle = BucleAplicacion(capturador, procesador, reconocedor, partida, num_regiones_jugador=2)
        bucle.procesar_un_frame()

        assert partida.mano_jugador.valor == 10
        assert partida.contador.running_count == -1

    def test_resultado_no_confiable_no_se_registra(self, mocks, partida):
        capturador, procesador, reconocedor = mocks
        procesador.detectar_regiones_candidatas.return_value = [region_falsa(0)]
        reconocedor.reconocer.return_value = ResultadoReconocimiento(rango=None, confianza=0.1)

        bucle = BucleAplicacion(capturador, procesador, reconocedor, partida, num_regiones_jugador=2)
        bucle.procesar_un_frame()

        assert partida.mano_jugador.valor == 0
        assert partida.contador.running_count == 0


class TestDeduplicacion:
    def test_mismo_frame_repetido_no_duplica_el_conteo(self, mocks, partida):
        capturador, procesador, reconocedor = mocks
        procesador.detectar_regiones_candidatas.return_value = [region_falsa(0)]
        reconocedor.reconocer.return_value = ResultadoReconocimiento(rango="10", confianza=0.95)

        bucle = BucleAplicacion(capturador, procesador, reconocedor, partida, num_regiones_jugador=2)

        for _ in range(5):  # el mismo frame "se procesa" 5 veces
            bucle.procesar_un_frame()

        assert partida.mano_jugador.valor == 10  # solo 1 carta, no 5
        assert partida.contador.running_count == -1  # contada una sola vez

    def test_carta_nueva_se_suma_sin_duplicar_la_anterior(self, mocks, partida):
        capturador, procesador, reconocedor = mocks
        bucle = BucleAplicacion(capturador, procesador, reconocedor, partida, num_regiones_jugador=2)

        # Frame 1: una sola carta
        procesador.detectar_regiones_candidatas.return_value = [region_falsa(0)]
        reconocedor.reconocer.return_value = ResultadoReconocimiento(rango="5", confianza=0.9)
        bucle.procesar_un_frame()
        bucle.procesar_un_frame()  # se repite, no deberia duplicar

        # Frame 3: aparece una segunda carta
        procesador.detectar_regiones_candidatas.return_value = [region_falsa(0), region_falsa(50)]
        reconocedor.reconocer.side_effect = [ResultadoReconocimiento(rango="6", confianza=0.9)]
        bucle.procesar_un_frame()

        assert partida.mano_jugador.valor == 11  # 5 + 6, ninguna duplicada
        assert partida.contador.running_count == 2  # +1 (el 5) +1 (el 6) = +2


class TestAsignacionJugadorCrupier:
    def test_regiones_se_dividen_segun_num_regiones_jugador(self, mocks, partida):
        capturador, procesador, reconocedor = mocks
        procesador.detectar_regiones_candidatas.return_value = [
            region_falsa(0), region_falsa(50), region_falsa(300),
        ]
        reconocedor.reconocer.side_effect = [
            ResultadoReconocimiento(rango="10", confianza=0.9),
            ResultadoReconocimiento(rango="6", confianza=0.9),
            ResultadoReconocimiento(rango="A", confianza=0.9),
        ]

        bucle = BucleAplicacion(capturador, procesador, reconocedor, partida, num_regiones_jugador=2)
        bucle.procesar_un_frame()

        assert partida.mano_jugador.valor == 16  # primeras 2 regiones
        assert partida.mano_crupier.valor == 11  # tercera region (A)


class TestCicloDeVida:
    def test_nueva_mano_resetea_contadores_de_deduplicacion(self, mocks, partida):
        capturador, procesador, reconocedor = mocks
        procesador.detectar_regiones_candidatas.return_value = [region_falsa(0)]
        reconocedor.reconocer.return_value = ResultadoReconocimiento(rango="5", confianza=0.9)

        bucle = BucleAplicacion(capturador, procesador, reconocedor, partida, num_regiones_jugador=2)
        bucle.procesar_un_frame()
        assert partida.mano_jugador.valor == 5

        bucle.nueva_mano()
        assert partida.mano_jugador.valor == 0
        assert partida.contador.running_count == 1  # el conteo se mantiene

        # Tras nueva_mano, la MISMA region (region_falsa(0)) debe poder
        # volver a registrarse, ya que el contador de deduplicacion se reinicio.
        bucle.procesar_un_frame()
        assert partida.mano_jugador.valor == 5
        assert partida.contador.running_count == 2  # se conto de nuevo, correctamente

    def test_nuevo_zapato_resetea_todo_incluido_running_count(self, mocks, partida):
        capturador, procesador, reconocedor = mocks
        procesador.detectar_regiones_candidatas.return_value = [region_falsa(0)]
        reconocedor.reconocer.return_value = ResultadoReconocimiento(rango="5", confianza=0.9)

        bucle = BucleAplicacion(capturador, procesador, reconocedor, partida, num_regiones_jugador=2)
        bucle.procesar_un_frame()

        bucle.nuevo_zapato()

        assert partida.mano_jugador.valor == 0
        assert partida.contador.running_count == 0
