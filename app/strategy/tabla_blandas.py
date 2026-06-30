"""
Tabla de estrategia basica: MANOS BLANDAS.

Una mano "blanda" es aquella donde el As se puede contar como 11 sin
pasarse de 21 (ej. A+6 = "blando 17", A+2 = "blando 13").

Notacion de filas: el valor que se usa es el TOTAL de la mano (con el
As como 11), igual que en Mano.valor. Asi, A+6 es 17, A+7 es 18, etc.
Solo existen manos blandas de 13 a 20 con 2 cartas (A+2 hasta A+9);
A+10 ya es blackjack (21) y se gestiona aparte.
"""

from __future__ import annotations

from app.strategy.reglas import Accion
from app.strategy.tabla_duras import CARTAS_CRUPIER

P = Accion.PEDIR
S = Accion.PLANTARSE
D = Accion.DOBLAR

# total_blando -> lista de acciones para cada carta del crupier (2..A)
_FILAS_BLANDAS = {
    13: [P, P, P, D, D, P, P, P, P, P],  # A+2
    14: [P, P, P, D, D, P, P, P, P, P],  # A+3
    15: [P, P, D, D, D, P, P, P, P, P],  # A+4
    16: [P, P, D, D, D, P, P, P, P, P],  # A+5
    17: [P, D, D, D, D, P, P, P, P, P],  # A+6
    18: [S, D, D, D, D, S, S, P, P, P],  # A+7
    19: [S, S, S, S, S, S, S, S, S, S],  # A+8
    20: [S, S, S, S, S, S, S, S, S, S],  # A+9
}

TABLA_BLANDAS: dict[tuple[int, str], Accion] = {}

for _total, _acciones in _FILAS_BLANDAS.items():
    for _carta, _accion in zip(CARTAS_CRUPIER, _acciones):
        TABLA_BLANDAS[(_total, _carta)] = _accion


def obtener_accion_blanda(total_jugador: int, rango_crupier: str) -> Accion:
    """
    Devuelve la accion recomendada para una mano blanda (con As=11).

    Args:
        total_jugador: valor total de la mano (Mano.valor), entre 13 y 20.
        rango_crupier: rango de la carta visible del crupier.
    """
    rango_normalizado = "10" if rango_crupier in ("10", "J", "Q", "K") else rango_crupier

    if total_jugador >= 21:
        # Blackjack natural (A+10): no hay decision, se gestiona aparte.
        return S
    if total_jugador < 13:
        # No deberia ocurrir con una mano blanda real (A+1 no existe),
        # pero por seguridad se trata como pedir.
        return P

    return TABLA_BLANDAS[(total_jugador, rango_normalizado)]
