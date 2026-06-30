"""
Selector visual de region de pantalla.

Permite al usuario elegir, arrastrando el mouse, el area de la
pantalla donde esta la mesa de blackjack. Corresponde a la
funcionalidad de Configuracion descrita en el documento del proyecto:
"Seleccion de la region de pantalla donde se encuentra la mesa".

Funcionamiento:
    1. Se abre una ventana transparente a pantalla completa, siempre
       encima de todo, que captura los eventos de mouse.
    2. Al presionar el boton del mouse y arrastrar, se dibuja un
       rectangulo semitransparente que sigue al cursor en tiempo real.
    3. Al soltar el mouse, la seleccion se confirma y la ventana se
       cierra.
    4. Si el usuario presiona Escape, la seleccion se cancela.

Esta clase NO sabe nada de captura, vision ni del resto del sistema:
solo produce (o no) una RegionPantalla. Es la unica responsabilidad
que tiene.
"""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QWidget

from app.capture.region import RegionPantalla

# Tamaño minimo (en pixeles) para aceptar una seleccion como valida.
# Evita producir una RegionPantalla de tamaño casi cero si el usuario
# solo hizo clic sin arrastrar.
TAMANO_MINIMO_PIXELES = 10


class SelectorRegion(QWidget):
    """Ventana transparente a pantalla completa para seleccionar una region con el mouse."""

    def __init__(self):
        super().__init__()
        self._punto_inicial: QPoint | None = None
        self._punto_actual: QPoint | None = None
        self._region_resultado: RegionPantalla | None = None
        self._fue_cancelado = False

        self._configurar_ventana()

    def _configurar_ventana(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        # Fondo translucido: se ve un velo oscuro sobre toda la pantalla,
        # para que sea evidente que se esta en "modo seleccion".
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.showFullScreen()

    # ------------------------------------------------------------------
    # Eventos de mouse y teclado
    # ------------------------------------------------------------------

    def mousePressEvent(self, evento: QMouseEvent) -> None:
        if evento.button() == Qt.MouseButton.LeftButton:
            self._punto_inicial = evento.position().toPoint()
            self._punto_actual = self._punto_inicial
            self.update()  # fuerza un repintado

    def mouseMoveEvent(self, evento: QMouseEvent) -> None:
        if self._punto_inicial is not None:
            self._punto_actual = evento.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, evento: QMouseEvent) -> None:
        if evento.button() == Qt.MouseButton.LeftButton and self._punto_inicial is not None:
            self._punto_actual = evento.position().toPoint()
            self._confirmar_seleccion()

    def keyPressEvent(self, evento: QKeyEvent) -> None:
        if evento.key() == Qt.Key.Key_Escape:
            self._fue_cancelado = True
            self.close()

    # ------------------------------------------------------------------
    # Logica de seleccion
    # ------------------------------------------------------------------

    def _rectangulo_actual(self) -> QRect:
        """Rectangulo normalizado entre el punto inicial y el actual (sin importar la direccion del arrastre)."""
        if self._punto_inicial is None or self._punto_actual is None:
            return QRect()
        return QRect(self._punto_inicial, self._punto_actual).normalized()

    def _confirmar_seleccion(self) -> None:
        rectangulo = self._rectangulo_actual()

        if rectangulo.width() < TAMANO_MINIMO_PIXELES or rectangulo.height() < TAMANO_MINIMO_PIXELES:
            # Seleccion demasiado pequeña: se ignora y se permite reintentar
            # (no se cierra la ventana, el usuario puede volver a arrastrar).
            self._punto_inicial = None
            self._punto_actual = None
            self.update()
            return

        self._region_resultado = RegionPantalla(
            x=rectangulo.x(),
            y=rectangulo.y(),
            ancho=rectangulo.width(),
            alto=rectangulo.height(),
        )
        self.close()

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------

    def paintEvent(self, evento) -> None:
        pintor = QPainter(self)

        # Velo oscuro semitransparente sobre toda la pantalla.
        pintor.fillRect(self.rect(), QColor(0, 0, 0, 100))

        rectangulo = self._rectangulo_actual()
        if not rectangulo.isNull():
            # La zona seleccionada se muestra "despejada" (sin velo) y
            # con un borde para que se distinga claramente.
            pintor.fillRect(rectangulo, QColor(0, 0, 0, 0))
            pintor.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            pintor.fillRect(rectangulo, QColor(255, 255, 255, 40))
            pintor.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            lapiz = QPen(QColor(0, 200, 255), 2)
            pintor.setPen(lapiz)
            pintor.drawRect(rectangulo)

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    @staticmethod
    def seleccionar() -> RegionPantalla | None:
        """
        Muestra el selector y bloquea hasta que el usuario complete o
        cancele la seleccion. Requiere que ya exista una QApplication
        en ejecucion.

        Returns:
            La RegionPantalla elegida, o None si el usuario cancelo
            (presionando Escape) o cerro la ventana sin seleccionar.
        """
        from PySide6.QtCore import QEventLoop

        selector = SelectorRegion()
        bucle_local = QEventLoop()
        selector.destroyed.connect(bucle_local.quit)
        bucle_local.exec()

        if selector._fue_cancelado:
            return None
        return selector._region_resultado
