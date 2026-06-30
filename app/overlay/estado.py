"""
Estado del overlay.

EstadoOverlay es un simple contenedor de datos con exactamente la
informacion que el overlay necesita mostrar en un momento dado. Es
deliberadamente independiente de PySide6/Qt: cualquier parte del
sistema (Partida, o un script de prueba) puede producir un
EstadoOverlay sin importar nada de Qt. Esto mantiene la logica de
negocio separada de la interfaz grafica.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.strategy.reglas import Accion


@dataclass
class EstadoOverlay:
    """Snapshot de la informacion a mostrar en la ventana flotante."""

    running_count: int = 0
    true_count: float = 0.0
    valor_mano_jugador: int = 0
    rango_carta_crupier: str | None = None
    recomendacion: Accion | None = None

    @property
    def texto_running_count(self) -> str:
        return f"{self.running_count:+d}"

    @property
    def texto_true_count(self) -> str:
        return f"{self.true_count:+.1f}"

    @property
    def texto_mano_jugador(self) -> str:
        return str(self.valor_mano_jugador) if self.valor_mano_jugador > 0 else "—"

    @property
    def texto_carta_crupier(self) -> str:
        return self.rango_carta_crupier if self.rango_carta_crupier else "—"

    @property
    def texto_recomendacion(self) -> str:
        return self.recomendacion.value if self.recomendacion else "—"

    @classmethod
    def desde_partida(cls, partida) -> "EstadoOverlay":
        """
        Construye un EstadoOverlay a partir del estado actual de una
        Partida (ver app.game.partida). Es el "puente" entre el motor
        de juego y la capa de presentacion.
        """
        rango_crupier = (
            partida.mano_crupier.cartas[0].rango if partida.mano_crupier.cartas else None
        )
        return cls(
            running_count=partida.contador.running_count,
            true_count=partida.contador.true_count,
            valor_mano_jugador=partida.mano_jugador.valor,
            rango_carta_crupier=rango_crupier,
            recomendacion=partida.recomendacion_actual(),
        )
