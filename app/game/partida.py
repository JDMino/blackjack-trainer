"""
Motor de juego: Partida.

Esta clase es el "orquestador central" del sistema (ver diagrama de
arquitectura del proyecto). Conecta:

    - Mano (jugador y crupier)
    - ContadorHiLo (conteo persistente durante el zapato)
    - MotorEstrategia (recomendacion segun la mano actual)

Partida NO sabe nada de captura de pantalla, vision por computadora
ni overlay. Solo expone metodos claros para "alimentar" cartas
observadas y "preguntar" la recomendacion actual. Esto permite
probarla por completo desde la consola, y mas adelante conectarla
con la capa de vision sin tener que modificar esta clase.
"""

from __future__ import annotations

from app.counting.hi_lo import ContadorHiLo
from app.models.carta import Carta
from app.models.mano import Mano
from app.strategy.motor import MotorEstrategia
from app.strategy.reglas import Accion, ReglasMesa


class Partida:
    """Representa el estado de una mano de blackjack en curso, junto con
    el conteo acumulado del zapato y el motor de estrategia."""

    def __init__(self, reglas: ReglasMesa | None = None):
        self.reglas = reglas or ReglasMesa()

        self.contador = ContadorHiLo(num_mazos=self.reglas.num_mazos)
        self.motor_estrategia = MotorEstrategia(reglas=self.reglas)

        self.mano_jugador = Mano()
        self.mano_crupier = Mano()

    # ------------------------------------------------------------------
    # Observacion de cartas: el unico punto de entrada de informacion.
    # ------------------------------------------------------------------

    def observar_carta_jugador(self, carta: Carta) -> None:
        """
        Registra una carta nueva vista en la mano del jugador.
        La carta se agrega a la mano Y se cuenta en el Hi-Lo (cada
        carta se cuenta exactamente una vez, segun la regla de negocio).
        """
        self.mano_jugador.agregar_carta(carta)
        self.contador.registrar_carta(carta)

    def observar_carta_crupier(self, carta: Carta) -> None:
        """Igual que observar_carta_jugador, pero para la mano del crupier."""
        self.mano_crupier.agregar_carta(carta)
        self.contador.registrar_carta(carta)

    # ------------------------------------------------------------------
    # Ciclo de vida de la partida.
    # ------------------------------------------------------------------

    def nueva_mano(self) -> None:
        """
        Empieza una mano nueva: limpia las manos del jugador y del
        crupier, pero MANTIENE el conteo Hi-Lo, ya que el conteo es
        valido durante todo el zapato, no solo durante una mano.
        """
        self.mano_jugador = Mano()
        self.mano_crupier = Mano()

    def nuevo_zapato(self) -> None:
        """
        Empieza un zapato (shoe) nuevo: reinicia el conteo Hi-Lo por
        completo, ademas de limpiar las manos actuales. Corresponde a
        la regla de negocio: 'el conteo debe reiniciarse cuando el
        usuario indique el comienzo de un nuevo mazo o zapato'.
        """
        self.contador.reiniciar()
        self.nueva_mano()

    # ------------------------------------------------------------------
    # Consulta de recomendacion.
    # ------------------------------------------------------------------

    def recomendacion_actual(self) -> Accion | None:
        """
        Devuelve la accion recomendada para la mano actual del jugador,
        o None si todavia no hay suficiente informacion (por ejemplo,
        si el crupier aun no tiene ninguna carta visible, o el jugador
        no tiene cartas).
        """
        if not self.mano_jugador.cartas or not self.mano_crupier.cartas:
            return None

        rango_crupier = self.mano_crupier.cartas[0].rango
        return self.motor_estrategia.recomendar(self.mano_jugador, rango_crupier)

    def __repr__(self) -> str:
        return (
            f"Partida(jugador={self.mano_jugador!r}, "
            f"crupier={self.mano_crupier!r}, "
            f"contador={self.contador!r})"
        )
