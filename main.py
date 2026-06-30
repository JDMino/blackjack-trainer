"""
Punto de entrada de Blackjack Trainer AI.

Al iniciar, pide al usuario seleccionar con el mouse la region de la
pantalla donde esta la mesa (ver app/overlay/selector_region.py).
Con esa region, conecta las 7 capas del proyecto (ver docs del
proyecto, seccion "Arquitectura") en un bucle continuo:

    Captura -> Procesamiento -> Reconocimiento -> Partida -> Overlay

CONFIGURACION:
    Los valores de configuracion (fps, rutas de plantillas, etc.)
    estan agrupados al inicio de main() para que sean faciles de
    ajustar sin tener que leer toda la logica del bucle. En una
    version futura (V2), estos valores se cargaran desde app/config/
    (JSON), tal como indica el documento del proyecto, en vez de
    estar fijos en el codigo.

COMO EJECUTAR:
    python main.py

    Requiere un entorno con pantalla grafica real (Windows, macOS, o
    Linux con escritorio). No funciona en un entorno sin pantalla.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from app.capture.capturador import CapturadorPantalla
from app.game.bucle_aplicacion import BucleAplicacion
from app.game.partida import Partida
from app.overlay.estado import EstadoOverlay
from app.overlay.selector_region import SelectorRegion
from app.overlay.ventana import VentanaOverlay
from app.recognition.banco_plantillas import BancoPlantillas
from app.recognition.reconocedor import ReconocedorCartas
from app.strategy.reglas import ReglasMesa
from app.vision.procesador import ProcesadorImagen


def main() -> int:
    # ------------------------------------------------------------------
    # CONFIGURACION (ajustar segun tu fuente de video real)
    # ------------------------------------------------------------------
    FPS_CAPTURA = 15
    CARPETA_PLANTILLAS = "assets/plantillas"
    NUM_REGIONES_JUGADOR = 2  # cuantas cartas detectadas (de izq. a der.) son del jugador
    INTERVALO_REFRESCO_MS = int(1000 / FPS_CAPTURA)
    REGLAS_MESA = ReglasMesa(num_mazos=6, permite_rendirse=False)

    # ------------------------------------------------------------------
    # QApplication debe existir antes de crear cualquier ventana de Qt,
    # incluyendo el selector de region.
    # ------------------------------------------------------------------
    app = QApplication(sys.argv)

    # ------------------------------------------------------------------
    # PASO 1: el usuario selecciona con el mouse donde esta la mesa.
    # ------------------------------------------------------------------
    print("Selecciona con el mouse la region de la mesa (Esc para cancelar)...")
    region = SelectorRegion.seleccionar()
    if region is None:
        print("Seleccion cancelada. Cerrando la aplicacion.")
        return 0
    print(f"Region seleccionada: {region}")

    # ------------------------------------------------------------------
    # PASO 2: construccion del resto de las capas, ya con la region.
    # ------------------------------------------------------------------
    banco_plantillas = BancoPlantillas()
    banco_plantillas.cargar_desde_carpeta(CARPETA_PLANTILLAS)
    if len(banco_plantillas) == 0:
        print(
            f"AVISO: no se encontraron plantillas en '{CARPETA_PLANTILLAS}'. "
            "El reconocedor no podra identificar ninguna carta hasta que "
            "agregues archivos '{rango}.png' en esa carpeta."
        )
        return 1

    capturador = CapturadorPantalla(region=region, fps=FPS_CAPTURA)
    procesador = ProcesadorImagen()
    reconocedor = ReconocedorCartas(banco=banco_plantillas, umbral_confianza=0.8)
    partida = Partida(reglas=REGLAS_MESA)

    bucle = BucleAplicacion(
        capturador=capturador,
        procesador=procesador,
        reconocedor=reconocedor,
        partida=partida,
        num_regiones_jugador=NUM_REGIONES_JUGADOR,
    )

    # ------------------------------------------------------------------
    # PASO 3: overlay + bucle continuo (QTimer no bloquea la ventana).
    # ------------------------------------------------------------------
    ventana = VentanaOverlay()

    def ciclo() -> None:
        """Se ejecuta periodicamente: procesa un frame y refresca el overlay."""
        bucle.procesar_un_frame()
        estado = EstadoOverlay.desde_partida(partida)
        ventana.actualizar(estado)

    temporizador = QTimer()
    temporizador.timeout.connect(ciclo)
    temporizador.start(INTERVALO_REFRESCO_MS)

    ventana.show()

    try:
        codigo_salida = app.exec()
    finally:
        temporizador.stop()
        capturador.cerrar()

    return codigo_salida

if __name__ == "__main__":
    sys.exit(main())
