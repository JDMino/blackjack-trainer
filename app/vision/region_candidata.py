"""
Modelo de salida del procesamiento de imagen: RegionCandidata.

Representa un area de la imagen que PODRIA ser una carta (segun su
forma y tamaño), junto con el recorte de la imagen correspondiente.
No dice que carta es -> eso es responsabilidad de app/recognition/,
que recibira estos recortes como entrada.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class RegionCandidata:
    """Un area rectangular detectada como posible carta, con su recorte de imagen."""

    x: int
    y: int
    ancho: int
    alto: int
    imagen: np.ndarray  # recorte de la imagen original correspondiente a esta region

    @property
    def proporcion(self) -> float:
        """Relacion alto/ancho del rectangulo. Las cartas reales suelen
        tener una proporcion cercana a 1.4 (mas altas que anchas)."""
        if self.ancho == 0:
            return 0.0
        return self.alto / self.ancho

    @property
    def area(self) -> int:
        return self.ancho * self.alto

    def __repr__(self) -> str:
        return (
            f"RegionCandidata(x={self.x}, y={self.y}, ancho={self.ancho}, "
            f"alto={self.alto}, proporcion={self.proporcion:.2f})"
        )
