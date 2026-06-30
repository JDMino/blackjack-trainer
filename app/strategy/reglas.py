"""
Definiciones compartidas del motor de estrategia: las acciones posibles
y las reglas de mesa configurables que afectan que estrategia es la
"correcta" (ej. si se permite rendirse, o si el crupier se planta en
soft 17).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Accion(str, Enum):
    """Las acciones que el motor de estrategia puede recomendar."""

    PEDIR = "Pedir"
    PLANTARSE = "Plantarse"
    DOBLAR = "Doblar"
    DIVIDIR = "Dividir"
    RENDIRSE = "Rendirse"

    def __str__(self) -> str:
        return self.value


@dataclass
class ReglasMesa:
    """
    Reglas configurables de la mesa que afectan la estrategia optima.
    Los valores por defecto son los mas comunes en mesas de casino
    con 6-8 mazos.
    """

    crupier_planta_en_soft_17: bool = True
    permite_doblar_despues_de_dividir: bool = True
    permite_rendirse: bool = False
    num_mazos: int = 6
