"""
Tests para app.overlay.ventana.VentanaOverlay.

Usa el fixture 'qapp' (definido en conftest.py) para tener una
QApplication disponible. Corre con QT_QPA_PLATFORM=offscreen
(tambien configurado en conftest.py), por lo que no requiere una
pantalla real.
"""

from PySide6.QtCore import Qt

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
        # 5 acciones distintas deberian producir 5 estilos (colores) distintos
        assert len(colores_vistos) == len(list(Accion))
