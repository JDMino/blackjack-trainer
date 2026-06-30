"""Tests para app.vision.procesador.ProcesadorImagen"""

import cv2
import numpy as np
import pytest

from app.vision.procesador import ProcesadorImagen


def crear_frame_con_rectangulos(rectangulos, alto=400, ancho=800):
    """
    Genera un frame BGRA sintetico con fondo oscuro y rectangulos
    blancos en las posiciones dadas. rectangulos es una lista de
    tuplas (x, y, ancho_rect, alto_rect).
    """
    frame = np.zeros((alto, ancho, 4), dtype=np.uint8)
    frame[:, :, :3] = 20
    frame[:, :, 3] = 255
    for x, y, w, h in rectangulos:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255, 255), -1)
    return frame


@pytest.fixture
def procesador():
    return ProcesadorImagen()


class TestFrameABgr:
    def test_convierte_bgra_a_bgr_quitando_canal_alfa(self, procesador):
        frame_bgra = np.zeros((10, 10, 4), dtype=np.uint8)
        resultado = procesador.frame_a_bgr(frame_bgra)
        assert resultado.shape == (10, 10, 3)


class TestDeteccionDeRegiones:
    def test_detecta_un_rectangulo_con_proporcion_de_carta(self, procesador):
        # 70x98 -> proporcion alto/ancho = 1.4, justo la esperada
        frame = crear_frame_con_rectangulos([(50, 50, 70, 98)])
        regiones = procesador.detectar_regiones_candidatas(frame)
        assert len(regiones) == 1
        assert regiones[0].proporcion == pytest.approx(1.4, abs=0.1)

    def test_detecta_varias_cartas_ordenadas_de_izquierda_a_derecha(self, procesador):
        frame = crear_frame_con_rectangulos(
            [(400, 50, 70, 98), (50, 50, 70, 98), (200, 50, 70, 98)]
        )
        regiones = procesador.detectar_regiones_candidatas(frame)
        assert len(regiones) == 3
        xs = [r.x for r in regiones]
        assert xs == sorted(xs)  # deben venir ordenadas de izq. a der.

    def test_descarta_formas_demasiado_pequenas(self, procesador):
        frame = crear_frame_con_rectangulos([(50, 50, 70, 98), (600, 300, 5, 5)])
        regiones = procesador.detectar_regiones_candidatas(frame)
        assert len(regiones) == 1  # la mancha pequeña no cuenta

    def test_descarta_formas_con_proporcion_incorrecta(self, procesador):
        # Rectangulo ancho y bajo: proporcion alto/ancho muy por debajo de 1.4
        frame = crear_frame_con_rectangulos([(50, 50, 70, 98), (550, 50, 150, 30)])
        regiones = procesador.detectar_regiones_candidatas(frame)
        assert len(regiones) == 1

    def test_frame_sin_nada_no_detecta_regiones(self, procesador):
        frame = crear_frame_con_rectangulos([])
        regiones = procesador.detectar_regiones_candidatas(frame)
        assert regiones == []

    def test_cada_region_tiene_un_recorte_de_imagen_valido(self, procesador):
        frame = crear_frame_con_rectangulos([(50, 50, 70, 98)])
        regiones = procesador.detectar_regiones_candidatas(frame)
        recorte = regiones[0].imagen
        assert recorte.shape[2] == 3  # BGR, sin canal alfa
        assert recorte.shape[0] > 0 and recorte.shape[1] > 0


class TestParametrosConfigurables:
    def test_area_minima_mas_alta_descarta_mas_formas(self):
        frame = crear_frame_con_rectangulos([(50, 50, 70, 98)])
        procesador_estricto = ProcesadorImagen(area_minima=10_000_000)
        regiones = procesador_estricto.detectar_regiones_candidatas(frame)
        assert len(regiones) == 0  # incluso la carta valida se descarta por area minima absurda
