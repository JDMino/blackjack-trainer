"""Tests para app.overlay.selector_region.SelectorRegion"""

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent

from app.overlay.selector_region import SelectorRegion, TAMANO_MINIMO_PIXELES


def evento_mouse(tipo, pos):
    return QMouseEvent(
        tipo, QPointF(pos), Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier,
    )


def evento_tecla(tecla):
    return QKeyEvent(QKeyEvent.Type.KeyPress, tecla, Qt.KeyboardModifier.NoModifier)


class TestArrastreValido:
    def test_arrastre_produce_la_region_esperada(self, qapp):
        selector = SelectorRegion()
        selector.mousePressEvent(evento_mouse(QMouseEvent.Type.MouseButtonPress, QPoint(100, 100)))
        selector.mouseMoveEvent(evento_mouse(QMouseEvent.Type.MouseMove, QPoint(250, 200)))
        selector.mouseReleaseEvent(evento_mouse(QMouseEvent.Type.MouseButtonRelease, QPoint(400, 300)))

        region = selector._region_resultado
        assert region is not None
        assert region.x == 100
        assert region.y == 100
        # +/-1 de tolerancia: QRect es inclusivo en ambos extremos.
        assert region.ancho in (300, 301)
        assert region.alto in (200, 201)

    def test_arrastre_en_direccion_inversa_se_normaliza(self, qapp):
        # Arrastrar de abajo-derecha hacia arriba-izquierda debe dar
        # la misma region que arrastrar al reves.
        selector = SelectorRegion()
        selector.mousePressEvent(evento_mouse(QMouseEvent.Type.MouseButtonPress, QPoint(400, 300)))
        selector.mouseReleaseEvent(evento_mouse(QMouseEvent.Type.MouseButtonRelease, QPoint(100, 100)))

        region = selector._region_resultado
        assert region.x in (100, 101)
        assert region.y in (100, 101)


class TestSeleccionDemasiadoPequena:
    def test_seleccion_pequena_se_rechaza_sin_cerrar(self, qapp):
        selector = SelectorRegion()
        selector.mousePressEvent(evento_mouse(QMouseEvent.Type.MouseButtonPress, QPoint(100, 100)))
        selector.mouseReleaseEvent(
            evento_mouse(QMouseEvent.Type.MouseButtonRelease, QPoint(100 + TAMANO_MINIMO_PIXELES - 1, 101))
        )

        assert selector._region_resultado is None
        assert selector._punto_inicial is None  # se resetea, listo para reintentar

    def test_tras_seleccion_pequena_se_puede_reintentar(self, qapp):
        selector = SelectorRegion()
        # Intento fallido (muy pequeño)
        selector.mousePressEvent(evento_mouse(QMouseEvent.Type.MouseButtonPress, QPoint(100, 100)))
        selector.mouseReleaseEvent(evento_mouse(QMouseEvent.Type.MouseButtonRelease, QPoint(102, 101)))
        assert selector._region_resultado is None

        # Reintento valido
        selector.mousePressEvent(evento_mouse(QMouseEvent.Type.MouseButtonPress, QPoint(50, 50)))
        selector.mouseReleaseEvent(evento_mouse(QMouseEvent.Type.MouseButtonRelease, QPoint(250, 150)))
        assert selector._region_resultado is not None


class TestCancelacion:
    def test_escape_marca_cancelado(self, qapp):
        selector = SelectorRegion()
        selector.keyPressEvent(evento_tecla(Qt.Key.Key_Escape))
        assert selector._fue_cancelado is True
        assert selector._region_resultado is None

    def test_otra_tecla_no_cancela(self, qapp):
        selector = SelectorRegion()
        selector.keyPressEvent(evento_tecla(Qt.Key.Key_A))
        assert selector._fue_cancelado is False
