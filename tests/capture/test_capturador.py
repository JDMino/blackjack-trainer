"""
Tests para app.capture.capturador.CapturadorPantalla.

Como mss requiere una pantalla real (un servidor X11/Wayland/Windows),
estos tests sustituyen (mock) la libreria mss por completo. Esto
permite verificar la LOGICA propia de CapturadorPantalla (como llama
a mss, como controla el FPS) sin depender de hardware grafico, algo
indispensable para correr esta suite en un servidor de CI.
"""

import time

import numpy as np
import pytest

from app.capture.capturador import CapturadorPantalla
from app.capture.region import RegionPantalla


@pytest.fixture
def region():
    return RegionPantalla(x=0, y=0, ancho=100, alto=100)


class TestConstruccion:
    def test_fps_cero_o_negativo_lanza_error(self, region):
        with pytest.raises(ValueError):
            CapturadorPantalla(region, fps=0)
        with pytest.raises(ValueError):
            CapturadorPantalla(region, fps=-5)

    def test_fps_por_defecto_es_quince(self, region):
        capturador = CapturadorPantalla(region)
        assert capturador.fps == 15


class TestCapturarFrame:
    def test_capturar_frame_usa_mss_con_la_region_correcta(self, region, mocker):
        frame_falso = np.zeros((100, 100, 4), dtype=np.uint8)

        mock_instancia_mss = mocker.MagicMock()
        mock_instancia_mss.grab.return_value = frame_falso
        mocker.patch("mss.mss", return_value=mock_instancia_mss)

        capturador = CapturadorPantalla(region)
        resultado = capturador.capturar_frame()

        # Verifica que se llamo a grab() con el diccionario correcto
        mock_instancia_mss.grab.assert_called_once_with(region.a_diccionario_mss())
        assert isinstance(resultado, np.ndarray)

    def test_la_instancia_de_mss_se_crea_una_sola_vez(self, region, mocker):
        mock_mss_constructor = mocker.patch("mss.mss")
        mock_mss_constructor.return_value.grab.return_value = np.zeros((100, 100, 4), dtype=np.uint8)

        capturador = CapturadorPantalla(region)
        capturador.capturar_frame()
        capturador.capturar_frame()
        capturador.capturar_frame()

        # mss.mss() (el constructor) solo debe llamarse una vez, no en cada captura.
        assert mock_mss_constructor.call_count == 1


class TestCerrar:
    def test_cerrar_libera_la_instancia_de_mss(self, region, mocker):
        mock_instancia_mss = mocker.MagicMock()
        mocker.patch("mss.mss", return_value=mock_instancia_mss)

        capturador = CapturadorPantalla(region)
        capturador.capturar_frame()  # crea la instancia interna
        capturador.cerrar()

        mock_instancia_mss.close.assert_called_once()
        assert capturador._sct is None

    def test_cerrar_sin_haber_capturado_nunca_no_falla(self, region):
        capturador = CapturadorPantalla(region)
        capturador.cerrar()  # no debe lanzar error aunque nunca se llamo a mss


class TestContextManager:
    def test_with_cierra_automaticamente(self, region, mocker):
        mock_instancia_mss = mocker.MagicMock()
        mocker.patch("mss.mss", return_value=mock_instancia_mss)

        with CapturadorPantalla(region) as capturador:
            capturador.capturar_frame()

        mock_instancia_mss.close.assert_called_once()


class TestFlujoDeFrames:
    def test_respeta_el_intervalo_de_fps(self, region, mocker):
        frame_falso = np.zeros((100, 100, 4), dtype=np.uint8)
        capturador = CapturadorPantalla(region, fps=10)
        mocker.patch.object(capturador, "capturar_frame", return_value=frame_falso)

        generador = capturador.flujo_de_frames()
        tiempos = []
        for _ in range(4):
            t0 = time.perf_counter()
            next(generador)
            tiempos.append(time.perf_counter() - t0)

        # Los frames 2, 3, 4 (no el primero) deben respetar ~0.1s de intervalo.
        for t in tiempos[1:]:
            assert t == pytest.approx(0.1, abs=0.03)

    def test_cada_frame_producido_es_el_esperado(self, region, mocker):
        frame_falso = np.ones((100, 100, 4), dtype=np.uint8)
        capturador = CapturadorPantalla(region, fps=100)  # fps alto para que el test sea rapido
        mocker.patch.object(capturador, "capturar_frame", return_value=frame_falso)

        generador = capturador.flujo_de_frames()
        primer_frame = next(generador)
        np.testing.assert_array_equal(primer_frame, frame_falso)
