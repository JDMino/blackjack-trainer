from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QCloseEvent, QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from app.overlay.estado import EstadoOverlay
from app.strategy.reglas import Accion


_COLORES_ACCION = {
    Accion.PEDIR: "#4CAF50",
    Accion.PLANTARSE: "#F44336",
    Accion.DOBLAR: "#FFC107",
    Accion.DIVIDIR: "#2196F3",
    Accion.RENDIRSE: "#9E9E9E",
}

_COLOR_SIN_DATOS = "#FFFFFF"


class VentanaOverlay(QWidget):
    """Ventana flotante arrastrable con botón para cerrar."""

    def __init__(self):
        super().__init__()

        self._drag_pos: QPoint | None = None

        self._configurar_ventana()
        self._construir_layout()
        self.actualizar(EstadoOverlay())

    # ------------------------------------------------------------------
    # Configuración
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

        self.resize(240, 250)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _construir_layout(self) -> None:

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Barra superior
        barra = QHBoxLayout()

        titulo = QLabel("Blackjack Trainer AI")
        titulo.setStyleSheet(
            "color:white;font-size:12px;font-weight:bold;"
        )

        barra.addWidget(titulo)
        barra.addStretch()

        boton_cerrar = QPushButton("✕")
        boton_cerrar.setFixedSize(22, 22)
        boton_cerrar.clicked.connect(self.close)

        boton_cerrar.setStyleSheet("""
            QPushButton{
                background:#C62828;
                color:white;
                border:none;
                border-radius:11px;
                font-weight:bold;
            }
            QPushButton:hover{
                background:#E53935;
            }
        """)

        barra.addWidget(boton_cerrar)

        layout.addLayout(barra)

        fuente_etiqueta = "color:#AAAAAA;font-size:12px;"
        fuente_valor = "color:white;font-size:20px;font-weight:bold;"

        self._titulo_rc = self._crear("RUNNING COUNT", fuente_etiqueta)
        self._valor_rc = self._crear("+0", fuente_valor)

        self._titulo_tc = self._crear("TRUE COUNT", fuente_etiqueta)
        self._valor_tc = self._crear("+0.0", fuente_valor)

        self._titulo_mano = self._crear("TU MANO", fuente_etiqueta)
        self._valor_mano = self._crear("—", fuente_valor)

        self._titulo_crupier = self._crear("CRUPIER", fuente_etiqueta)
        self._valor_crupier = self._crear("—", fuente_valor)

        self._titulo_rec = self._crear("RECOMENDACIÓN", fuente_etiqueta)
        self._valor_rec = self._crear(
            "—",
            "color:white;font-size:22px;font-weight:bold;",
        )

        for w in (
            self._titulo_rc,
            self._valor_rc,
            self._titulo_tc,
            self._valor_tc,
            self._titulo_mano,
            self._valor_mano,
            self._titulo_crupier,
            self._valor_crupier,
            self._titulo_rec,
            self._valor_rec,
        ):
            layout.addWidget(w)

    def _crear(self, texto: str, estilo: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setStyleSheet(estilo)
        return lbl

    # ------------------------------------------------------------------
    # Arrastrar la ventana
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self._drag_pos is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint() - self._drag_pos
            )

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None

    # ------------------------------------------------------------------
    # Actualización
    # ------------------------------------------------------------------

    def actualizar(self, estado: EstadoOverlay) -> None:

        self._valor_rc.setText(estado.texto_running_count)
        self._valor_tc.setText(estado.texto_true_count)
        self._valor_mano.setText(estado.texto_mano_jugador)
        self._valor_crupier.setText(estado.texto_carta_crupier)
        self._valor_rec.setText(estado.texto_recomendacion)

        color = (
            _COLORES_ACCION.get(
                estado.recomendacion,
                _COLOR_SIN_DATOS,
            )
            if estado.recomendacion
            else _COLOR_SIN_DATOS
        )

        self._valor_rec.setStyleSheet(
            f"color:{color};font-size:22px;font-weight:bold;"
        )

    # ------------------------------------------------------------------
    # Cierre
    # ------------------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        QApplication.instance().quit()
        event.accept()