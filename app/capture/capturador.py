"""
Capturador de pantalla.

Esta clase envuelve la libreria 'mss' para capturar continuamente una
RegionPantalla. Es la unica parte del sistema que sabe que existe
'mss'; si en el futuro se cambiara de libreria de captura, solo este
archivo deberia modificarse.

Notas de diseño:
    - Cada captura devuelve un array de NumPy en formato BGRA (el que
      usa mss por defecto), listo para pasarse a OpenCV (que se usara
      en la capa de vision) sin conversiones adicionales costosas.
    - La libreria mss requiere crear una instancia por hilo/proceso;
      por eso CapturadorPantalla crea su propia instancia interna y
      no la comparte.
"""

from __future__ import annotations

import time
from collections.abc import Iterator

import mss
import numpy as np

from app.capture.region import RegionPantalla


class CapturadorPantalla:
    """Captura continuamente una region de pantalla a una frecuencia configurable."""

    def __init__(self, region: RegionPantalla, fps: int = 15):
        """
        Args:
            region: area de la pantalla a capturar.
            fps: capturas por segundo deseadas (el documento del
                 proyecto sugiere 10-20 fps).
        """
        if fps <= 0:
            raise ValueError("fps debe ser mayor que 0")

        self.region = region
        self.fps = fps
        self._sct: mss.base.MSSBase | None = None

    def _asegurar_instancia_mss(self) -> mss.base.MSSBase:
        """Crea la instancia de mss de forma diferida (lazy), solo cuando se necesita."""
        if self._sct is None:
            self._sct = mss.mss()
        return self._sct

    def capturar_frame(self) -> np.ndarray:
        """
        Captura un unico frame de la region configurada y lo devuelve
        como array de NumPy con forma (alto, ancho, 4) en formato BGRA.
        """
        sct = self._asegurar_instancia_mss()
        captura = sct.grab(self.region.a_diccionario_mss())
        # mss.grab devuelve un objeto ScreenShot; np.array lo convierte
        # directamente a un array BGRA listo para procesar.
        return np.array(captura)

    def flujo_de_frames(self) -> Iterator[np.ndarray]:
        """
        Generador infinito que produce frames a la frecuencia (fps)
        configurada. Pensado para usarse en un bucle:

            for frame in capturador.flujo_de_frames():
                procesar(frame)

        Se detiene solo si el consumidor deja de iterar (ej. con
        'break') o si se interrumpe el programa.
        """
        intervalo_segundos = 1.0 / self.fps

        while True:
            inicio = time.perf_counter()

            yield self.capturar_frame()

            transcurrido = time.perf_counter() - inicio
            tiempo_de_espera = intervalo_segundos - transcurrido
            if tiempo_de_espera > 0:
                time.sleep(tiempo_de_espera)

    def cerrar(self) -> None:
        """Libera los recursos de la instancia de mss. Llamar al terminar de capturar."""
        if self._sct is not None:
            self._sct.close()
            self._sct = None

    def __enter__(self) -> "CapturadorPantalla":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.cerrar()
