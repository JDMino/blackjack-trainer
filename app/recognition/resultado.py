"""
Modelo de salida del reconocimiento: ResultadoReconocimiento.

Representa el veredicto del ReconocedorCartas para un recorte de
imagen dado: que rango se identifico y con que nivel de confianza.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResultadoReconocimiento:
    """Veredicto del reconocedor para un recorte: rango detectado y confianza."""

    rango: str | None  # None si no se pudo reconocer con confianza suficiente
    confianza: float  # entre 0.0 (nada de parecido) y 1.0 (coincidencia perfecta)

    @property
    def es_confiable(self) -> bool:
        """True si hay un rango identificado (no None)."""
        return self.rango is not None

    def __repr__(self) -> str:
        if self.rango is None:
            return f"ResultadoReconocimiento(SIN RECONOCER, confianza={self.confianza:.2f})"
        return f"ResultadoReconocimiento(rango={self.rango!r}, confianza={self.confianza:.2f})"
