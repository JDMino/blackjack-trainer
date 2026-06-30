"""
Reconocedor de cartas.

Compara un recorte de imagen (proveniente de app.vision, una
RegionCandidata) contra todas las plantillas de un BancoPlantillas
usando template matching de OpenCV, y devuelve el rango cuya
plantilla tuvo mayor coincidencia.
"""

from __future__ import annotations

import cv2
import numpy as np

from app.recognition.banco_plantillas import BancoPlantillas, TAMANO_PLANTILLA
from app.recognition.resultado import ResultadoReconocimiento


class ReconocedorCartas:
    """Identifica el rango de una carta comparando su imagen contra un banco de plantillas."""

    def __init__(self, banco: BancoPlantillas, umbral_confianza: float = 0.6):
        """
        Args:
            banco: banco de plantillas ya cargado con al menos un rango.
            umbral_confianza: confianza minima (0.0-1.0) para aceptar
                              un resultado como valido. Por debajo de
                              este umbral, se devuelve rango=None en
                              vez de arriesgar una recomendacion de
                              estrategia basada en una lectura dudosa.
        """
        if len(banco) == 0:
            raise ValueError("El banco de plantillas esta vacio; carga al menos una plantilla")
        if not (0.0 <= umbral_confianza <= 1.0):
            raise ValueError("umbral_confianza debe estar entre 0.0 y 1.0")

        self.banco = banco
        self.umbral_confianza = umbral_confianza

    def reconocer(self, imagen_recorte_bgr: np.ndarray) -> ResultadoReconocimiento:
        """
        Compara el recorte dado contra todas las plantillas disponibles
        y devuelve el rango con mejor coincidencia, si supera el umbral
        de confianza configurado.
        """
        imagen_normalizada = self._normalizar(imagen_recorte_bgr)

        mejor_rango: str | None = None
        mejor_puntaje = -1.0

        for rango in self.banco.rangos_disponibles:
            plantilla = self.banco.obtener_plantilla(rango)
            puntaje = self._comparar(imagen_normalizada, plantilla)
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_rango = rango

        if mejor_puntaje < self.umbral_confianza:
            return ResultadoReconocimiento(rango=None, confianza=mejor_puntaje)

        return ResultadoReconocimiento(rango=mejor_rango, confianza=mejor_puntaje)

    def _normalizar(self, imagen_bgr: np.ndarray) -> np.ndarray:
        """Convierte a escala de grises y redimensiona al tamaño estandar de plantilla."""
        if imagen_bgr.ndim == 3:
            gris = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2GRAY)
        else:
            gris = imagen_bgr  # ya viene en escala de grises
        return cv2.resize(gris, TAMANO_PLANTILLA)

    def _comparar(self, imagen: np.ndarray, plantilla: np.ndarray) -> float:
        """
        Calcula que tan parecidas son dos imagenes del mismo tamaño
        usando correlacion normalizada (cv2.TM_CCOEFF_NORMED), que
        devuelve un valor entre -1.0 y 1.0 (1.0 = coincidencia perfecta).
        Se recorta a 0.0 como minimo para que sea interpretable como
        una "confianza" simple.
        """
        resultado = cv2.matchTemplate(imagen, plantilla, cv2.TM_CCOEFF_NORMED)
        puntaje = float(resultado[0][0])
        return max(puntaje, 0.0)
