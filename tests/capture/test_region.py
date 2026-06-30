"""Tests para app.capture.region.RegionPantalla"""

import pytest

from app.capture.region import RegionPantalla


class TestConstruccion:
    def test_construccion_valida(self):
        region = RegionPantalla(x=10, y=20, ancho=300, alto=200)
        assert region.x == 10
        assert region.y == 20
        assert region.ancho == 300
        assert region.alto == 200

    @pytest.mark.parametrize("ancho", [0, -1, -100])
    def test_ancho_invalido_lanza_error(self, ancho):
        with pytest.raises(ValueError):
            RegionPantalla(x=0, y=0, ancho=ancho, alto=100)

    @pytest.mark.parametrize("alto", [0, -1, -100])
    def test_alto_invalido_lanza_error(self, alto):
        with pytest.raises(ValueError):
            RegionPantalla(x=0, y=0, ancho=100, alto=alto)

    def test_x_negativo_lanza_error(self):
        with pytest.raises(ValueError):
            RegionPantalla(x=-1, y=0, ancho=100, alto=100)

    def test_y_negativo_lanza_error(self):
        with pytest.raises(ValueError):
            RegionPantalla(x=0, y=-1, ancho=100, alto=100)

    def test_x_e_y_en_cero_son_validos(self):
        region = RegionPantalla(x=0, y=0, ancho=100, alto=100)
        assert region.x == 0
        assert region.y == 0


class TestConversionMss:
    def test_a_diccionario_mss(self):
        region = RegionPantalla(x=10, y=20, ancho=300, alto=200)
        assert region.a_diccionario_mss() == {
            "left": 10,
            "top": 20,
            "width": 300,
            "height": 200,
        }
