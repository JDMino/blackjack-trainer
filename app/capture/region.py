"""
Modelo de configuracion: RegionPantalla.

Representa el area de la pantalla que se va a capturar (donde esta
la mesa de blackjack). Es un simple contenedor de datos: no sabe nada
de mss, opencv ni de como se captura realmente la imagen. Esto permite
que mas adelante un selector visual (con Qt) simplemente necesite
producir un objeto de esta clase, sin acoplarse a la libreria de
captura usada por debajo.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RegionPantalla:
    """Area rectangular de la pantalla a capturar, en pixeles."""

    x: int
    y: int
    ancho: int
    alto: int

    def __post_init__(self) -> None:
        if self.ancho <= 0 or self.alto <= 0:
            raise ValueError("ancho y alto deben ser mayores que 0")
        if self.x < 0 or self.y < 0:
            raise ValueError("x e y no pueden ser negativos")

    def a_diccionario_mss(self) -> dict:
        """
        Convierte la region al formato de diccionario que espera la
        libreria mss para definir el area de captura: {'left', 'top',
        'width', 'height'}.
        """
        return {"left": self.x, "top": self.y, "width": self.ancho, "height": self.alto}

    def __repr__(self) -> str:
        return f"RegionPantalla(x={self.x}, y={self.y}, ancho={self.ancho}, alto={self.alto})"
