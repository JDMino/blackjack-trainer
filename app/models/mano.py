"""
Modelo de dominio: Mano.

Una Mano es una coleccion de Cartas (la del jugador o la del crupier)
que sabe calcular su propio valor total, incluyendo la regla especial
del As (vale 11, pero si eso hace que la mano se pase de 21, se cuenta
como 1).
"""

from __future__ import annotations

from app.models.carta import Carta


class Mano:
    """Representa una mano de blackjack (del jugador o del crupier)."""

    def __init__(self, cartas: list[Carta] | None = None):
        # Usamos una lista interna propia; si no se pasa nada, empieza vacia.
        self.cartas: list[Carta] = list(cartas) if cartas else []

    def agregar_carta(self, carta: Carta) -> None:
        self.cartas.append(carta)

    @property
    def valor(self) -> int:
        """
        Valor total de la mano aplicando la regla del As.

        Se suman todas las cartas tratando al As como 11. Despues,
        mientras la mano se pase de 21 y todavia haya al menos un As
        "sin bajar", se resta 10 (equivalente a tratar ese As como 1).
        """
        total = sum(carta.valor for carta in self.cartas)
        ases_como_11 = sum(1 for carta in self.cartas if carta.es_as)

        while total > 21 and ases_como_11 > 0:
            total -= 10  # bajamos un As de 11 a 1
            ases_como_11 -= 1

        return total

    @property
    def es_blanda(self) -> bool:
        """
        True si la mano es 'blanda' (soft): contiene un As que todavia
        se esta contando como 11 sin que la mano se pase de 21.
        Esto es relevante para la estrategia basica (ej. 'mano blanda 18').
        """
        total_con_ases_altos = sum(carta.valor for carta in self.cartas)
        tiene_as = any(carta.es_as for carta in self.cartas)
        return tiene_as and total_con_ases_altos <= 21

    @property
    def es_par(self) -> bool:
        """True si la mano tiene exactamente 2 cartas del mismo rango (para decidir 'dividir')."""
        return len(self.cartas) == 2 and self.cartas[0].rango == self.cartas[1].rango

    @property
    def es_blackjack(self) -> bool:
        """True si la mano son 2 cartas que suman 21 (As + figura/10)."""
        return len(self.cartas) == 2 and self.valor == 21

    @property
    def se_pasó(self) -> bool:
        """True si la mano supera 21 (bust)."""
        return self.valor > 21

    def __repr__(self) -> str:
        cartas_str = ", ".join(str(c) for c in self.cartas)
        return f"Mano([{cartas_str}] -> valor={self.valor})"
