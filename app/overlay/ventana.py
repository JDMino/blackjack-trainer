"""
Ventana flotante (overlay) construida con PySide6.

Muestra de forma continua: running count, true count, la mano del
jugador, la carta visible del crupier y la recomendacion actual.

Controles:
    - Arrastrar con el mouse: mover la ventana por la pantalla.
    - Boton "Nueva mano": avisa al motor de juego que empezo una mano nueva
      (limpia las manos pero mantiene el conteo Hi-Lo del zapato).
    - Boton "Nuevo zapato": reinicia el conteo Hi-Lo por completo.
    - Boton X: cierra la aplicacion.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QCloseEvent, QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.overlay.estado import EstadoOverlay
from app.strategy.reglas import Accion

# Colores por accion, para que la recomendacion resalte visualmente.
_COLORES_ACCION = {
    Accion.PEDIR:     "#4CAF50",  # verde
    Accion.PLANTARSE: "#F44336",  # rojo
    Accion.DOBLAR:    "#FFC107",  # amarillo
    Accion.DIVIDIR:   "#2196F3",  # azul
    Accion.RENDIRSE:  "#9E9E9E",  # gris
}
_COLOR_SIN_DATOS = "#FFFFFF"


class VentanaOverlay(QWidget):
    """Ventana flotante arrastrable con botones de control de partida."""

    def __init__(
        self,
        on_nueva_mano: Callable[[], None] | None = None,
        on_nuevo_zapato: Callable[[], None] | None = None,
    ):
        """
        Args:
            on_nueva_mano: callback que se llama cuando el usuario pulsa
                           "Nueva mano". Tipicamente: bucle.nueva_mano().
            on_nuevo_zapato: callback para "Nuevo zapato". Tipicamente:
                             bucle.nuevo_zapato().
        """
        super().__init__()
        self._on_nueva_mano = on_nueva_mano or (lambda: None)
        self._on_nuevo_zapato = on_nuevo_zapato or (lambda: None)
        self._drag_pos: QPoint | None = None

        self._configurar_ventana()
        self._construir_layout()
        self.actualizar(EstadoOverlay())  # estado inicial vacio

    # ------------------------------------------------------------------
    # Configuracion
    # ------------------------------------------------------------------

    def _configurar_ventana(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                border-radius: 8px;
            }
        """)
        self.resize(240, 280)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _construir_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        # --- Barra superior: titulo + boton cerrar ---
        barra = QHBoxLayout()
        titulo = QLabel("Blackjack Trainer AI")
        titulo.setStyleSheet("color: white; font-size: 11px; font-weight: bold;")
        barra.addWidget(titulo)
        barra.addStretch()

        btn_cerrar = QPushButton("✕")
        btn_cerrar.setFixedSize(20, 20)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background: #C62828; color: white;
                border: none; border-radius: 10px; font-weight: bold; font-size: 10px;
            }
            QPushButton:hover { background: #E53935; }
        """)
        btn_cerrar.clicked.connect(self.close)
        barra.addWidget(btn_cerrar)
        layout.addLayout(barra)

        # --- Datos de conteo y mano ---
        etq = "color: #AAAAAA; font-size: 11px;"
        val = "color: white; font-size: 19px; font-weight: bold;"

        self._titulo_rc   = self._etiqueta("RUNNING COUNT", etq)
        self._valor_rc    = self._etiqueta("+0", val)
        self._titulo_tc   = self._etiqueta("TRUE COUNT", etq)
        self._valor_tc    = self._etiqueta("+0.0", val)
        self._titulo_mano = self._etiqueta("TU MANO", etq)
        self._valor_mano  = self._etiqueta("—", val)
        self._titulo_crupier  = self._etiqueta("CRUPIER", etq)
        self._valor_crupier   = self._etiqueta("—", val)
        self._titulo_rec  = self._etiqueta("RECOMENDACIÓN", etq)
        self._valor_recomendacion = self._etiqueta(
            "—", "color: white; font-size: 21px; font-weight: bold;"
        )

        for w in (
            self._titulo_rc, self._valor_rc,
            self._titulo_tc, self._valor_tc,
            self._titulo_mano, self._valor_mano,
            self._titulo_crupier, self._valor_crupier,
            self._titulo_rec, self._valor_recomendacion,
        ):
            layout.addWidget(w)

        # --- Botones de control ---
        layout.addSpacing(6)
        fila_botones = QHBoxLayout()
        fila_botones.setSpacing(6)

        estilo_boton = """
            QPushButton {{
                background: {bg}; color: white;
                border: none; border-radius: 4px;
                font-size: 11px; font-weight: bold;
                padding: 5px 4px;
            }}
            QPushButton:hover {{ background: {hover}; }}
            QPushButton:pressed {{ background: {pressed}; }}
        """

        self._btn_nueva_mano = QPushButton("Nueva mano")
        self._btn_nueva_mano.setStyleSheet(
            estilo_boton.format(bg="#1565C0", hover="#1976D2", pressed="#0D47A1")
        )
        self._btn_nueva_mano.clicked.connect(self._on_nueva_mano)

        self._btn_nuevo_zapato = QPushButton("Nuevo zapato")
        self._btn_nuevo_zapato.setStyleSheet(
            estilo_boton.format(bg="#6A1B9A", hover="#7B1FA2", pressed="#4A148C")
        )
        self._btn_nuevo_zapato.clicked.connect(self._on_nuevo_zapato)

        fila_botones.addWidget(self._btn_nueva_mano)
        fila_botones.addWidget(self._btn_nuevo_zapato)
        layout.addLayout(fila_botones)

    def _etiqueta(self, texto: str, estilo: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setStyleSheet(estilo)
        return lbl

    # ------------------------------------------------------------------
    # Arrastrar la ventana
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None

    # ------------------------------------------------------------------
    # Actualizar datos
    # ------------------------------------------------------------------

    def actualizar(self, estado: EstadoOverlay) -> None:
        """Refresca todos los textos segun el EstadoOverlay recibido."""
        self._valor_rc.setText(estado.texto_running_count)
        self._valor_tc.setText(estado.texto_true_count)
        self._valor_mano.setText(estado.texto_mano_jugador)
        self._valor_crupier.setText(estado.texto_carta_crupier)
        self._valor_recomendacion.setText(estado.texto_recomendacion)

        color = (
            _COLORES_ACCION.get(estado.recomendacion, _COLOR_SIN_DATOS)
            if estado.recomendacion
            else _COLOR_SIN_DATOS
        )
        self._valor_recomendacion.setStyleSheet(
            f"color: {color}; font-size: 21px; font-weight: bold;"
        )

    # ------------------------------------------------------------------
    # Cierre
    # ------------------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        QApplication.instance().quit()
        event.accept()
