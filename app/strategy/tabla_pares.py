"""
Tabla de estrategia basica: PARES (decision de Dividir).

Cubre los pares 2-2 hasta A-A. Para pares de 10 (10-10, J-J, Q-Q, K-K,
o combinaciones entre ellas) la estrategia estandar es NUNCA dividir
(un total de 20 es demasiado bueno para arriesgarlo), por lo que no
se incluyen como un "par especial": simplemente no aparecen en esta
tabla y la decision recae en la tabla de manos duras (20 siempre es
Plantarse).

Cuando esta tabla indica que NO se debe dividir, devuelve None para
indicar "esta tabla no aplica una recomendacion de Dividir"; el
codigo que orquesta la decision debe entonces consultar la tabla de
duras o blandas segun corresponda.
"""

from __future__ import annotations

from app.strategy.reglas import Accion, ReglasMesa
from app.strategy.tabla_duras import CARTAS_CRUPIER

DIV = Accion.DIVIDIR
NO_DIVIDIR = None  # senal de "consultar la tabla normal (dura/blanda)"

# rango_del_par -> lista de "Dividir" o None para cada carta del crupier (2..A)
_FILAS_PARES = {
    "2": [DIV, DIV, DIV, DIV, DIV, DIV, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR],
    "3": [DIV, DIV, DIV, DIV, DIV, DIV, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR],
    "4": [NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR, DIV, DIV, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR],
    "5": [NO_DIVIDIR] * 10,  # 5-5 nunca se divide (se trata como duro 10: doblar)
    "6": [DIV, DIV, DIV, DIV, DIV, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR],
    "7": [DIV, DIV, DIV, DIV, DIV, DIV, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR, NO_DIVIDIR],
    "8": [DIV, DIV, DIV, DIV, DIV, DIV, DIV, DIV, DIV, DIV],  # 8-8 siempre se divide
    "9": [DIV, DIV, DIV, DIV, DIV, NO_DIVIDIR, DIV, DIV, NO_DIVIDIR, NO_DIVIDIR],
    "A": [DIV, DIV, DIV, DIV, DIV, DIV, DIV, DIV, DIV, DIV],  # A-A siempre se divide
}

TABLA_PARES: dict[tuple[str, str], Accion | None] = {}

for _rango_par, _acciones in _FILAS_PARES.items():
    for _carta, _accion in zip(CARTAS_CRUPIER, _acciones):
        TABLA_PARES[(_rango_par, _carta)] = _accion


def obtener_accion_par(
    rango_par: str, rango_crupier: str, reglas: ReglasMesa | None = None
) -> Accion | None:
    """
    Devuelve Accion.DIVIDIR si la estrategia basica recomienda dividir
    este par contra la carta del crupier, o None si no se debe dividir
    (en cuyo caso hay que consultar la tabla de duras/blandas).

    Args:
        rango_par: rango de las 2 cartas del par ("2".."9","10"/"J"/"Q"/"K","A").
        rango_crupier: rango de la carta visible del crupier.
        reglas: reglas de mesa (reservado para futuras variantes,
                ej. mesas donde 10-10 si se permite dividir).
    """
    rango_par_normalizado = "10" if rango_par in ("10", "J", "Q", "K") else rango_par
    rango_crupier_normalizado = "10" if rango_crupier in ("10", "J", "Q", "K") else rango_crupier

    # Los pares de 10 nunca se dividen en estrategia basica estandar.
    if rango_par_normalizado == "10":
        return None

    return TABLA_PARES.get((rango_par_normalizado, rango_crupier_normalizado), None)
