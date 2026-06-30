"""
Procesamiento de imagen.

Recibe un frame crudo (tal como lo entrega CapturadorPantalla, en
formato BGRA) y lo prepara para el reconocimiento de cartas:

    1. Convierte el frame a escala de grises y aplica un umbral
       (threshold) para separar las cartas (claras) del fondo del
       tapete (generalmente oscuro/verde).
    2. Encuentra los contornos de las formas resultantes.
    3. Filtra esos contornos para quedarse solo con los que tienen
       tamaño y proporcion compatibles con una carta real.
    4. Recorta la imagen original en cada region candidata.

Esta clase NO identifica que carta es cada recorte; eso es
responsabilidad de app/recognition/.
"""

from __future__ import annotations

import cv2
import numpy as np

from app.vision.region_candidata import RegionCandidata

# Proporcion (alto/ancho) esperada de una carta estandar de poker/blackjack.
# Una carta tipica es aproximadamente 1.4 veces mas alta que ancha.
PROPORCION_CARTA_ESPERADA = 1.4
TOLERANCIA_PROPORCION = 0.5  # margen de tolerancia alrededor del valor esperado


class ProcesadorImagen:
    """Convierte un frame crudo en una lista de RegionCandidata (posibles cartas)."""

    def __init__(
        self,
        area_minima: int = 2000,
        area_maxima: int = 200_000,
        umbral_binario: int = 150,
    ):
        """
        Args:
            area_minima: area minima (en pixeles^2) para considerar un
                         contorno como posible carta. Descarta ruido pequeño.
            area_maxima: area maxima permitida. Descarta formas demasiado
                         grandes (ej. todo el tapete detectado como un bloque).
            umbral_binario: valor de corte (0-255) usado para separar
                            las cartas (claras) del fondo (oscuro) tras
                            convertir a escala de grises. Puede necesitar
                            ajuste segun la iluminacion y el tapete real.
        """
        self.area_minima = area_minima
        self.area_maxima = area_maxima
        self.umbral_binario = umbral_binario

    def frame_a_bgr(self, frame_bgra: np.ndarray) -> np.ndarray:
        """Convierte un frame BGRA (formato de mss) a BGR (formato estandar de OpenCV)."""
        return cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)

    def detectar_regiones_candidatas(self, frame_bgra: np.ndarray) -> list[RegionCandidata]:
        """
        Pipeline completo: recibe un frame crudo y devuelve la lista
        de regiones candidatas a ser cartas, ordenadas de izquierda a
        derecha (util mas adelante para distinguir cartas del jugador
        de las del crupier por su posicion).
        """
        frame_bgr = self.frame_a_bgr(frame_bgra)
        mascara_binaria = self._a_mascara_binaria(frame_bgr)
        contornos = self._encontrar_contornos(mascara_binaria)
        candidatas = self._filtrar_y_recortar(contornos, frame_bgr)

        # Ordenar de izquierda a derecha por la coordenada x.
        candidatas.sort(key=lambda c: c.x)
        return candidatas

    def _a_mascara_binaria(self, frame_bgr: np.ndarray) -> np.ndarray:
        """
        Convierte el frame a una imagen binaria (blanco/negro) donde
        las zonas claras (probablemente cartas, que suelen tener fondo
        blanco) quedan en blanco y el resto en negro.
        """
        gris = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        # Suavizado leve para reducir ruido antes del umbral.
        gris_suavizado = cv2.GaussianBlur(gris, (5, 5), 0)
        _, mascara = cv2.threshold(
            gris_suavizado, self.umbral_binario, 255, cv2.THRESH_BINARY
        )
        return mascara

    def _encontrar_contornos(self, mascara_binaria: np.ndarray) -> list[np.ndarray]:
        """Encuentra los contornos externos de las formas en la mascara binaria."""
        contornos, _ = cv2.findContours(
            mascara_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return list(contornos)

    def _filtrar_y_recortar(
        self, contornos: list[np.ndarray], frame_bgr: np.ndarray
    ) -> list[RegionCandidata]:
        """
        Filtra los contornos por area y proporcion (alto/ancho) para
        quedarse solo con los que razonablemente podrian ser una carta,
        y recorta la imagen original en cada una de esas regiones.
        """
        candidatas: list[RegionCandidata] = []

        for contorno in contornos:
            x, y, ancho, alto = cv2.boundingRect(contorno)
            area = ancho * alto

            if area < self.area_minima or area > self.area_maxima:
                continue

            proporcion = alto / ancho if ancho > 0 else 0.0
            limite_inferior = PROPORCION_CARTA_ESPERADA - TOLERANCIA_PROPORCION
            limite_superior = PROPORCION_CARTA_ESPERADA + TOLERANCIA_PROPORCION
            if not (limite_inferior <= proporcion <= limite_superior):
                continue

            recorte = frame_bgr[y : y + alto, x : x + ancho].copy()
            candidatas.append(
                RegionCandidata(x=x, y=y, ancho=ancho, alto=alto, imagen=recorte)
            )

        return candidatas
