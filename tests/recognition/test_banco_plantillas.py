"""Tests para app.recognition.banco_plantillas.BancoPlantillas"""

import cv2
import numpy as np
import pytest

from app.recognition.banco_plantillas import BancoPlantillas, TAMANO_PLANTILLA


def imagen_gris_de_prueba(ancho=20, alto=30):
    return np.full((alto, ancho), 128, dtype=np.uint8)


class TestRegistrarPlantilla:
    def test_registrar_plantilla_valida(self):
        banco = BancoPlantillas()
        banco.registrar_plantilla("7", imagen_gris_de_prueba())
        assert "7" in banco.rangos_disponibles
        assert len(banco) == 1

    def test_rango_invalido_lanza_error(self):
        banco = BancoPlantillas()
        with pytest.raises(ValueError):
            banco.registrar_plantilla("99", imagen_gris_de_prueba())

    def test_plantilla_se_normaliza_al_tamano_estandar(self):
        banco = BancoPlantillas()
        banco.registrar_plantilla("7", imagen_gris_de_prueba(ancho=100, alto=200))
        plantilla = banco.obtener_plantilla("7")
        assert plantilla.shape == (TAMANO_PLANTILLA[1], TAMANO_PLANTILLA[0])

    def test_registrar_sobrescribe_plantilla_existente(self):
        banco = BancoPlantillas()
        banco.registrar_plantilla("7", imagen_gris_de_prueba())
        banco.registrar_plantilla("7", imagen_gris_de_prueba(ancho=50, alto=50))
        assert len(banco) == 1  # sigue siendo 1 rango, no se duplico


class TestObtenerPlantilla:
    def test_obtener_plantilla_inexistente_devuelve_none(self):
        banco = BancoPlantillas()
        assert banco.obtener_plantilla("A") is None

    def test_obtener_plantilla_existente(self):
        banco = BancoPlantillas()
        banco.registrar_plantilla("A", imagen_gris_de_prueba())
        assert banco.obtener_plantilla("A") is not None


class TestCargarDesdeCarpeta:
    def test_carpeta_inexistente_lanza_error(self):
        banco = BancoPlantillas()
        with pytest.raises(FileNotFoundError):
            banco.cargar_desde_carpeta("/ruta/que/no/existe/jamas")

    def test_carga_archivos_validos_e_ignora_faltantes(self, tmp_path):
        # tmp_path es un fixture de pytest: crea una carpeta temporal
        # unica para este test, que se borra automaticamente despues.
        cv2.imwrite(str(tmp_path / "7.png"), imagen_gris_de_prueba())
        cv2.imwrite(str(tmp_path / "A.png"), imagen_gris_de_prueba())
        # No se crea Q.png, J.png, etc. a proposito.

        banco = BancoPlantillas()
        banco.cargar_desde_carpeta(tmp_path)

        assert len(banco) == 2
        assert "7" in banco.rangos_disponibles
        assert "A" in banco.rangos_disponibles
        assert "Q" not in banco.rangos_disponibles

    def test_carpeta_vacia_resulta_en_banco_vacio(self, tmp_path):
        banco = BancoPlantillas()
        banco.cargar_desde_carpeta(tmp_path)
        assert len(banco) == 0


class TestRepr:
    def test_repr_no_lanza_error(self):
        banco = BancoPlantillas()
        banco.registrar_plantilla("7", imagen_gris_de_prueba())
        assert "7" in repr(banco)
