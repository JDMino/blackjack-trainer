"""
Banco de plantillas.

Carga y administra las imagenes de referencia (plantillas) usadas
para reconocer el rango de una carta por comparacion directa. Cada
plantilla es una imagen pequeña (tipicamente el indice de la esquina
de la carta: el numero o letra) asociada a un rango.

En esta primera version (ver documento del proyecto: "inicialmente
se utilizara un conjunto limitado de diseños de cartas"), se asume
UN solo diseño de baraja: una plantilla por rango es suficiente.
Version futura (V2): soportar multiples plantillas por rango para
reconocer distintos diseños de cartas.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from app.models.carta import RANGOS_VALIDOS

# Tamaño estandar al que se redimensionan todas las plantillas y los
# recortes a comparar, para que template matching siempre compare
# imagenes del mismo tamaño.
TAMANO_PLANTILLA = (40, 60)  # (ancho, alto) en pixeles


class BancoPlantillas:
    """Carga y mantiene en memoria las plantillas de referencia, una por rango."""

    def __init__(self):
        # rango -> imagen de plantilla (en escala de grises, tamaño normalizado)
        self._plantillas: dict[str, np.ndarray] = {}

    def cargar_desde_carpeta(self, carpeta: str | Path) -> None:
        """
        Carga las plantillas desde una carpeta donde cada archivo se
        llama '{rango}.png' (ej. '2.png', 'J.png', 'A.png').

        Args:
            carpeta: ruta a la carpeta que contiene los archivos de plantilla.
        """
        carpeta = Path(carpeta)
        if not carpeta.is_dir():
            raise FileNotFoundError(f"Carpeta de plantillas no encontrada: {carpeta}")

        for rango in RANGOS_VALIDOS:
            ruta_archivo = carpeta / f"{rango}.png"
            if not ruta_archivo.exists():
                continue  # se permite tener un conjunto incompleto, por ahora
            imagen = cv2.imread(str(ruta_archivo), cv2.IMREAD_GRAYSCALE)
            if imagen is None:
                continue
            self.registrar_plantilla(rango, imagen)

    def registrar_plantilla(self, rango: str, imagen_gris: np.ndarray) -> None:
        """
        Registra una plantilla para un rango especifico, normalizando
        su tamaño para que sea comparable con cualquier recorte.

        Args:
            rango: el rango al que corresponde esta plantilla ("2".."10","J","Q","K","A").
            imagen_gris: imagen en escala de grises (un solo canal) de la plantilla.
        """
        if rango not in RANGOS_VALIDOS:
            raise ValueError(f"Rango invalido: {rango!r}")

        imagen_normalizada = cv2.resize(imagen_gris, TAMANO_PLANTILLA)
        self._plantillas[rango] = imagen_normalizada

    def obtener_plantilla(self, rango: str) -> np.ndarray | None:
        return self._plantillas.get(rango)

    @property
    def rangos_disponibles(self) -> list[str]:
        return list(self._plantillas.keys())

    def __len__(self) -> int:
        return len(self._plantillas)

    def __repr__(self) -> str:
        return f"BancoPlantillas({len(self._plantillas)} rangos cargados: {sorted(self._plantillas.keys())})"
