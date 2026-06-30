"""
Tabla de estrategia basica: MANOS DURAS.

Una mano "dura" es aquella sin As, o con As contado obligatoriamente
como 1 (porque contarlo como 11 se pasaria de 21). Ejemplos: 10+6=16,
o A+6+10=17 (aqui el As ya vale 1, es dura).

La tabla cubre los totales 5 a 21. En la practica, los totales bajos
(5-8) siempre son "Pedir" y el 21 siempre es "Plantarse", pero se
incluyen explicitamente para que la tabla sea completa y facil de
auditar contra una fuente de referencia.

Claves del diccionario: (valor_mano, rango_carta_crupier) -> Accion
El rango de la carta del crupier se normaliza así: "10" cubre tambien
J, Q, K (todas valen 10 y la estrategia es identica).
"""

from __future__ import annotations

from app.strategy.reglas import Accion

# Cartas del crupier que se usan como columnas de la tabla.
CARTAS_CRUPIER = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "A")

P = Accion.PEDIR
S = Accion.PLANTARSE
D = Accion.DOBLAR
R = Accion.RENDIRSE

# Cada fila es el total duro del jugador (8 a 17; 18-21 siempre Plantarse,
# 5-7 siempre Pedir, por eso no se listan fila por fila pero se generan
# mas abajo para que la tabla quede completa).
_FILAS_8_A_17 = {
    8:  [P, P, P, P, P, P, P, P, P, P],
    9:  [P, D, D, D, D, P, P, P, P, P],
    10: [D, D, D, D, D, D, D, D, P, P],
    11: [D, D, D, D, D, D, D, D, D, P],
    12: [P, P, S, S, S, P, P, P, P, P],
    13: [S, S, S, S, S, P, P, P, P, P],
    14: [S, S, S, S, S, P, P, P, P, P],
    15: [S, S, S, S, S, P, P, P, R, R],
    16: [S, S, S, S, S, P, P, R, R, R],
    17: [S, S, S, S, S, S, S, S, S, S],
}

TABLA_DURAS: dict[tuple[int, str], Accion] = {}

# Totales 5, 6, 7: siempre Pedir, contra cualquier carta del crupier.
for _total in (5, 6, 7):
    for _carta in CARTAS_CRUPIER:
        TABLA_DURAS[(_total, _carta)] = P

# Totales 8 a 17: segun la tabla detallada arriba.
for _total, _acciones in _FILAS_8_A_17.items():
    for _carta, _accion in zip(CARTAS_CRUPIER, _acciones):
        TABLA_DURAS[(_total, _carta)] = _accion

# Totales 18 a 21: siempre Plantarse.
for _total in (18, 19, 20, 21):
    for _carta in CARTAS_CRUPIER:
        TABLA_DURAS[(_total, _carta)] = S


def obtener_accion_dura(total_jugador: int, rango_crupier: str) -> Accion:
    """
    Devuelve la accion recomendada para una mano dura.

    Args:
        total_jugador: valor total de la mano (ya calculado por Mano.valor).
        rango_crupier: rango de la carta visible del crupier ("2".."10","J","Q","K","A").
    """
    rango_normalizado = "10" if rango_crupier in ("10", "J", "Q", "K") else rango_crupier

    # Por debajo de 5 no hay decision real de estrategia (no deberia ocurrir
    # con 2 cartas, pero por seguridad devolvemos Pedir).
    if total_jugador < 5:
        return P
    if total_jugador > 21:
        # La mano ya se paso; no hay accion de estrategia que aplicar.
        return S

    return TABLA_DURAS[(total_jugador, rango_normalizado)]
