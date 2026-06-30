"""
Tests para app.overlay.ventana.VentanaOverlay.

Usa el fixture 'qapp' (definido en conftest.py) para tener una
QApplication disponible. Corre con QT_QPA_PLATFORM=offscreen
(tambien configurado en conftest.py), por lo que no requiere una
pantalla real.
"""

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent

from app.overlay.estado import EstadoOverlay
from app.overlay.ventana import VentanaOverlay
from app.strategy.reglas import Accion


class TestConstruccion:
    def test_ventana_se_construye_sin_error(self, qapp):
        ventana = VentanaOverlay()
        assert ventana is not None

    def test_estado_inicial_muestra_guiones_y_ceros(self, qapp):
        ventana = VentanaOverlay()
        assert ventana._valor_rc.text() == "+0"
        assert ventana._valor_mano.text() == "—"
        assert ventana._valor_recomendacion.text() == "—"

    def test_flags_de_ventana_flotante(self, qapp):
        ventana = VentanaOverlay()
        flags = ventana.windowFlags()
        assert bool(flags & Qt.WindowType.FramelessWindowHint) is True
        assert bool(flags & Qt.WindowType.WindowStaysOnTopHint) is True


class TestActualizar:
    def test_actualizar_refleja_el_estado_en_los_textos(self, qapp):
        ventana = VentanaOverlay()
        estado = EstadoOverlay(
            running_count=6,
            true_count=2.3,
            valor_mano_jugador=16,
            rango_carta_crupier="10",
            recomendacion=Accion.PEDIR,
        )
        ventana.actualizar(estado)

        assert ventana._valor_rc.text() == "+6"
        assert ventana._valor_tc.text() == "+2.3"
        assert ventana._valor_mano.text() == "16"
        assert ventana._valor_crupier.text() == "10"
        assert ventana._valor_recomendacion.text() == "Pedir"

    def test_actualizar_dos_veces_refleja_solo_el_ultimo_estado(self, qapp):
        ventana = VentanaOverlay()
        ventana.actualizar(EstadoOverlay(valor_mano_jugador=16))
        ventana.actualizar(EstadoOverlay(valor_mano_jugador=20))
        assert ventana._valor_mano.text() == "20"

    def test_cada_accion_tiene_un_color_distinto(self, qapp):
        ventana = VentanaOverlay()
        colores_vistos = set()
        for accion in Accion:
            ventana.actualizar(EstadoOverlay(recomendacion=accion))
            colores_vistos.add(ventana._valor_recomendacion.styleSheet())
        assert len(colores_vistos) == len(list(Accion))


class TestBotonesDeControl:
    def test_click_nueva_mano_dispara_callback(self, qapp):
        llamadas = []
        ventana = VentanaOverlay(on_nueva_mano=lambda: llamadas.append("nueva_mano"))
        ventana._btn_nueva_mano.click()
        assert llamadas == ["nueva_mano"]

    def test_click_nuevo_zapato_dispara_callback(self, qapp):
        llamadas = []
        ventana = VentanaOverlay(on_nuevo_zapato=lambda: llamadas.append("nuevo_zapato"))
        ventana._btn_nuevo_zapato.click()
        assert llamadas == ["nuevo_zapato"]

    def test_sin_callbacks_los_botones_no_lanzan_error(self, qapp):
        # Si no se pasan callbacks, los botones no deben romper nada
        ventana = VentanaOverlay()
        ventana._btn_nueva_mano.click()
        ventana._btn_nuevo_zapato.click()

    def test_nueva_mano_no_dispara_nuevo_zapato(self, qapp):
        llamadas = []
        ventana = VentanaOverlay(
            on_nueva_mano=lambda: llamadas.append("mano"),
            on_nuevo_zapato=lambda: llamadas.append("zapato"),
        )
        ventana._btn_nueva_mano.click()
        assert llamadas == ["mano"]  # solo uno, no los dos


class TestArrastre:
    def test_press_registra_posicion_de_arrastre(self, qapp):
        ventana = VentanaOverlay()
        ventana.show()
        evento = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPointF(QPoint(50, 50)),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        ventana.mousePressEvent(evento)
        assert ventana._drag_pos is not None

    def test_release_limpia_posicion_de_arrastre(self, qapp):
        ventana = VentanaOverlay()
        ventana.show()
        press = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPointF(QPoint(50, 50)),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        release = QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            QPointF(QPoint(50, 50)),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        ventana.mousePressEvent(press)
        ventana.mouseReleaseEvent(release)
        assert ventana._drag_pos is None
