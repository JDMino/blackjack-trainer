"""
Motor de estrategia basica.

Esta clase es el "orquestador": recibe la mano del jugador y la carta
visible del crupier, decide que tabla consultar (pares, blandas o
duras) y devuelve una Accion.

Tambien se encarga de "degradar" la accion ideal a una valida cuando
la situacion real no permite la accion de libro. Por ejemplo, la
tabla puede decir "Doblar", pero doblar solo es posible con exactamente
2 cartas; si el jugador ya pidio una carta extra, hay que degradar
esa recomendacion a Pedir o Plantarse.
"""

from __future__ import annotations

from app.models.mano import Mano
from app.strategy.reglas import Accion, ReglasMesa
from app.strategy.tabla_blandas import obtener_accion_blanda
from app.strategy.tabla_duras import obtener_accion_dura
from app.strategy.tabla_pares import obtener_accion_par


class MotorEstrategia:
    """Calcula la accion recomendada segun la estrategia basica."""

    def __init__(self, reglas: ReglasMesa | None = None):
        self.reglas = reglas or ReglasMesa()

    def recomendar(self, mano_jugador: Mano, rango_crupier: str) -> Accion:
        """
        Devuelve la accion recomendada para la mano actual del jugador
        contra la carta visible del crupier.

        Args:
            mano_jugador: la mano del jugador (Mano).
            rango_crupier: rango de la carta visible del crupier
                           ("2".."10","J","Q","K","A").
        """
        if mano_jugador.es_blackjack:
            return Accion.PLANTARSE  # nada que decidir, ya es 21 con 2 cartas

        accion_ideal = self._accion_ideal(mano_jugador, rango_crupier)
        return self._degradar_si_es_necesario(accion_ideal, mano_jugador)

    def _accion_ideal(self, mano_jugador: Mano, rango_crupier: str) -> Accion:
        """Consulta la tabla correspondiente SIN considerar restricciones de numero de cartas."""

        # 1. Si es un par y la mano tiene exactamente 2 cartas, se consulta
        #    primero la tabla de pares (dividir tiene prioridad si aplica).
        if mano_jugador.es_par:
            rango_par = mano_jugador.cartas[0].rango
            accion_par = obtener_accion_par(rango_par, rango_crupier, self.reglas)
            if accion_par is not None:
                return accion_par
            # Si la tabla de pares dice "no dividir", se sigue evaluando
            # como mano dura o blanda normalmente (ej. 5-5 se trata como duro 10).

        # 2. Mano blanda (As contado como 11).
        if mano_jugador.es_blanda:
            return obtener_accion_blanda(mano_jugador.valor, rango_crupier)

        # 3. Mano dura (caso por defecto).
        return obtener_accion_dura(mano_jugador.valor, rango_crupier)

    def _degradar_si_es_necesario(self, accion: Accion, mano_jugador: Mano) -> Accion:
        """
        Ajusta la accion ideal a una accion fisicamente valida segun
        cuantas cartas tiene la mano y las reglas de mesa configuradas.
        """
        num_cartas = len(mano_jugador.cartas)

        if accion == Accion.DOBLAR and num_cartas != 2:
            # Solo se puede doblar con la mano inicial de 2 cartas.
            # Se degrada a Pedir o Plantarse segun el valor actual.
            return Accion.PEDIR if mano_jugador.valor < 17 else Accion.PLANTARSE

        if accion == Accion.DIVIDIR and num_cartas != 2:
            # No deberia ocurrir en la practica (solo se evalua dividir
            # con 2 cartas), pero se protege igual.
            return Accion.PEDIR if mano_jugador.valor < 17 else Accion.PLANTARSE

        if accion == Accion.RENDIRSE:
            if not self.reglas.permite_rendirse or num_cartas != 2:
                # Si la mesa no permite rendirse, se degrada a la
                # siguiente mejor opcion conocida: Pedir (regla general
                # para las manos donde la tabla sugiere rendirse).
                return Accion.PEDIR

        return accion
