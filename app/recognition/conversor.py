"""
Conversor de resultados de reconocimiento a objetos Carta.

ReconocedorCartas solo identifica el RANGO de una carta (no el palo,
ya que el palo no afecta ni al conteo Hi-Lo ni a la estrategia
basica). Sin embargo, el modelo Carta del dominio exige un palo.

Para no romper el contrato de Carta ni inventar logica de reconocimiento
de palos (fuera del alcance del MVP, ver documento del proyecto:
"version futura V2"), se asigna un palo placeholder fijo. Esto es una
limitacion conocida y documentada: el palo mostrado/almacenado no es
fiable, pero no afecta ninguna decision de conteo o estrategia, que
dependen unicamente del rango.
"""

from __future__ import annotations

from app.models.carta import Carta
from app.recognition.resultado import ResultadoReconocimiento

# Palo placeholder: se usa porque el reconocedor actual no identifica
# el palo real. No afecta al conteo Hi-Lo ni a la estrategia basica.
PALO_PLACEHOLDER = "picas"


def resultado_a_carta(resultado: ResultadoReconocimiento) -> Carta | None:
    """
    Convierte un ResultadoReconocimiento en un objeto Carta, o None
    si el resultado no fue confiable (rango=None).
    """
    if not resultado.es_confiable:
        return None
    return Carta(rango=resultado.rango, palo=PALO_PLACEHOLDER)
