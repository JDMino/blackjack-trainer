"""Tests para app.recognition.reconocedor.ReconocedorCartas"""

import cv2
import numpy as np
import pytest

from app.recognition.banco_plantillas import BancoPlantillas
from app.recognition.reconocedor import ReconocedorCartas


def imagen_con_texto(texto, ancho=40, alto=60):
    """Genera una imagen en escala de grises con un texto dibujado, como una plantilla simple."""
    img = np.full((alto, ancho), 255, dtype=np.uint8)
    cv2.putText(img, texto, (2, alto - 15), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,), 2, cv2.LINE_AA)
    return img


@pytest.fixture
def banco_con_plantillas():
    banco = BancoPlantillas()
    for rango in ["2", "7", "A"]:
        banco.registrar_plantilla(rango, imagen_con_texto(rango))
    return banco


class TestConstruccion:
    def test_banco_vacio_lanza_error(self):
        banco_vacio = BancoPlantillas()
        with pytest.raises(ValueError):
            ReconocedorCartas(banco_vacio)

    @pytest.mark.parametrize("umbral", [-0.1, 1.1, 2.0])
    def test_umbral_fuera_de_rango_lanza_error(self, banco_con_plantillas, umbral):
        with pytest.raises(ValueError):
            ReconocedorCartas(banco_con_plantillas, umbral_confianza=umbral)

    @pytest.mark.parametrize("umbral", [0.0, 0.5, 1.0])
    def test_umbral_en_rango_valido_es_aceptado(self, banco_con_plantillas, umbral):
        reconocedor = ReconocedorCartas(banco_con_plantillas, umbral_confianza=umbral)
        assert reconocedor.umbral_confianza == umbral


class TestReconocer:
    def test_imagen_identica_a_plantilla_se_reconoce_con_alta_confianza(self, banco_con_plantillas):
        reconocedor = ReconocedorCartas(banco_con_plantillas, umbral_confianza=0.6)
        imagen_bgr = cv2.cvtColor(imagen_con_texto("7"), cv2.COLOR_GRAY2BGR)

        resultado = reconocedor.reconocer(imagen_bgr)

        assert resultado.rango == "7"
        assert resultado.confianza == pytest.approx(1.0, abs=0.01)
        assert resultado.es_confiable is True

    def test_imagen_de_ruido_puro_no_se_reconoce(self, banco_con_plantillas):
        reconocedor = ReconocedorCartas(banco_con_plantillas, umbral_confianza=0.6)
        rng = np.random.default_rng(seed=42)
        ruido = rng.integers(0, 256, (60, 40), dtype=np.uint8)
        imagen_bgr = cv2.cvtColor(ruido, cv2.COLOR_GRAY2BGR)

        resultado = reconocedor.reconocer(imagen_bgr)

        assert resultado.rango is None
        assert resultado.es_confiable is False

    def test_acepta_imagen_en_escala_de_grises_directamente(self, banco_con_plantillas):
        reconocedor = ReconocedorCartas(banco_con_plantillas, umbral_confianza=0.6)
        imagen_gris = imagen_con_texto("A")

        resultado = reconocedor.reconocer(imagen_gris)

        assert resultado.rango == "A"

    def test_umbral_mas_estricto_rechaza_coincidencias_debiles(self, banco_con_plantillas):
        # Un umbral muy alto (0.99) debe rechazar incluso coincidencias razonables
        # si no son perfectas. Usamos una imagen ligeramente distinta (con ruido).
        reconocedor = ReconocedorCartas(banco_con_plantillas, umbral_confianza=0.99)
        rng = np.random.default_rng(seed=1)
        imagen_con_ruido = imagen_con_texto("2").astype(np.int16)
        imagen_con_ruido += rng.integers(-30, 30, imagen_con_ruido.shape)
        imagen_con_ruido = np.clip(imagen_con_ruido, 0, 255).astype(np.uint8)

        resultado = reconocedor.reconocer(imagen_con_ruido)

        assert resultado.confianza < 0.99
