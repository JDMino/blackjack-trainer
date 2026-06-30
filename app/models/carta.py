"""
Modelo de dominio: Carta.

Representa una carta individual de la baraja. No depende de ningun
otro modulo (ni de vision, ni de captura): es un objeto "puro" que
solo sabe describirse a si mismo y calcular su propio valor.
"""

from __future__ import annotations

# Rangos validos de una carta estandar (sin jokers).
RANGOS_VALIDOS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")

# Palos validos.
PALOS_VALIDOS = ("corazones", "diamantes", "treboles", "picas")

# Valor base de cada rango para el calculo de la mano.
# El As se trata aparte (puede valer 1 u 11), por eso aqui vale 11
# como valor "alto" por defecto.
_VALORES_BASE = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "10": 10, "J": 10, "Q": 10, "K": 10,
    "A": 11,
}


class Carta:
    """Representa una carta de la baraja (ej. 'A de corazones')."""

    def __init__(self, rango: str, palo: str):
        if rango not in RANGOS_VALIDOS:
            raise ValueError(f"Rango invalido: {rango!r}. Validos: {RANGOS_VALIDOS}")
        if palo not in PALOS_VALIDOS:
            raise ValueError(f"Palo invalido: {palo!r}. Validos: {PALOS_VALIDOS}")

        self.rango = rango
        self.palo = palo

    @property
    def valor(self) -> int:
        """Valor numerico de la carta (As = 11 por defecto; ver Mano para el ajuste a 1)."""
        return _VALORES_BASE[self.rango]

    @property
    def es_as(self) -> bool:
        return self.rango == "A"

    @property
    def es_figura_o_diez(self) -> bool:
        """True para 10, J, Q, K (todas valen 10)."""
        return self.rango in ("10", "J", "Q", "K")

    def __repr__(self) -> str:
        return f"Carta({self.rango!r}, {self.palo!r})"

    def __str__(self) -> str:
        return f"{self.rango} de {self.palo}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Carta):
            return NotImplemented
        return self.rango == other.rango and self.palo == other.palo
