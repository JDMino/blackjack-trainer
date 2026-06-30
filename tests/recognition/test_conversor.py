"""Tests para app.recognition.conversor"""

from app.models.carta import Carta
from app.recognition.conversor import resultado_a_carta
from app.recognition.resultado import ResultadoReconocimiento


class TestResultadoACarta:
    def test_resultado_confiable_se_convierte_en_carta(self):
        resultado = ResultadoReconocimiento(rango="7", confianza=0.9)
        carta = resultado_a_carta(resultado)
        assert isinstance(carta, Carta)
        assert carta.rango == "7"

    def test_resultado_no_confiable_devuelve_none(self):
        resultado = ResultadoReconocimiento(rango=None, confianza=0.2)
        assert resultado_a_carta(resultado) is None
