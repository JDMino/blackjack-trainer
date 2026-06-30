"""
Bucle principal de la aplicacion.

BucleAplicacion conecta, frame por frame, las capas de:

    Captura -> Procesamiento -> Reconocimiento -> Partida (Conteo+Estrategia)

Su responsabilidad mas importante es la DEDUPLICACION: la captura
corre a 10-20 fps, por lo que una misma carta fisica aparecera en
decenas de frames consecutivos. Sin deduplicar, una carta se contaria
muchas veces en el Hi-Lo, violando la regla de negocio del proyecto
("cada carta debe contarse una sola vez por mano").

Estrategia de deduplicacion usada (MVP):
    Se asume que las cartas reconocidas en un frame, ordenadas de
    izquierda a derecha, corresponden en orden a como fueron repartidas.
    Si en el frame actual se reconocen MAS cartas de las que ya se
    tenian registradas para esa mano, las cartas "nuevas" (las que
    estan en las posiciones que faltaban) se registran en Partida.
    Esto asume que las cartas no desaparecen ni se reordenan entre
    frames, lo cual es razonable para un MVP con una sola mesa fija.
"""

from __future__ import annotations

from app.capture.capturador import CapturadorPantalla
from app.game.partida import Partida
from app.recognition.conversor import resultado_a_carta
from app.recognition.reconocedor import ReconocedorCartas
from app.vision.procesador import ProcesadorImagen


class BucleAplicacion:
    """Orquesta captura, vision, reconocimiento y el motor de juego, frame por frame."""

    def __init__(
        self,
        capturador: CapturadorPantalla,
        procesador: ProcesadorImagen,
        reconocedor: ReconocedorCartas,
        partida: Partida,
        num_regiones_jugador: int,
    ):
        """
        Args:
            capturador: fuente de frames de pantalla.
            procesador: detecta regiones candidatas a carta en cada frame.
            reconocedor: identifica el rango de cada region candidata.
            partida: motor de juego a alimentar con las cartas nuevas.
            num_regiones_jugador: cuantas de las regiones candidatas
                (de izquierda a derecha) corresponden al jugador; el
                resto se asignan al crupier. Es una simplificacion de
                MVP: asume una disposicion fija de la mesa en pantalla.
                Una version futura (V2) podria detectar esto automaticamente.
        """
        self.capturador = capturador
        self.procesador = procesador
        self.reconocedor = reconocedor
        self.partida = partida
        self.num_regiones_jugador = num_regiones_jugador

        # Cuantas cartas ya se registraron en Partida para la mano actual,
        # para poder detectar cuales son "nuevas" en el siguiente frame.
        self._cartas_jugador_registradas = 0
        self._cartas_crupier_registradas = 0

    def procesar_un_frame(self) -> None:
        """
        Captura un unico frame y, si hay cartas nuevas reconocidas con
        confianza suficiente, las registra en la Partida. Pensado para
        llamarse en un bucle continuo (ver ejecutar()).
        """
        frame = self.capturador.capturar_frame()
        regiones = self.procesador.detectar_regiones_candidatas(frame)

        regiones_jugador = regiones[: self.num_regiones_jugador]
        regiones_crupier = regiones[self.num_regiones_jugador :]

        self._cartas_jugador_registradas = self._registrar_cartas_nuevas(
            regiones_jugador,
            ya_registradas=self._cartas_jugador_registradas,
            observar=self.partida.observar_carta_jugador,
        )
        self._cartas_crupier_registradas = self._registrar_cartas_nuevas(
            regiones_crupier,
            ya_registradas=self._cartas_crupier_registradas,
            observar=self.partida.observar_carta_crupier,
        )

    def _registrar_cartas_nuevas(self, regiones, ya_registradas, observar) -> int:
        """
        Reconoce cada region y registra en Partida solo las cartas que
        estan mas alla de las ya registradas (deduplicacion por conteo
        de posicion, ver docstring del modulo).

        Devuelve el nuevo total de cartas registradas, para que el
        llamador actualice su contador correspondiente.
        """
        if len(regiones) <= ya_registradas:
            return ya_registradas  # no hay cartas nuevas que registrar en este frame

        regiones_nuevas = regiones[ya_registradas:]
        cartas_reconocidas_ok = 0

        for region in regiones_nuevas:
            resultado = self.reconocedor.reconocer(region.imagen)
            carta = resultado_a_carta(resultado)
            if carta is None:
                # No se reconocio con confianza suficiente: no se cuenta
                # todavia. Se reintentara en el siguiente frame, ya que
                # la misma carta fisica seguira apareciendo.
                continue
            observar(carta)
            cartas_reconocidas_ok += 1

        return ya_registradas + cartas_reconocidas_ok

    def nueva_mano(self) -> None:
        """Reinicia el conteo de deduplicacion y delega en Partida.nueva_mano()."""
        self._cartas_jugador_registradas = 0
        self._cartas_crupier_registradas = 0
        self.partida.nueva_mano()

    def nuevo_zapato(self) -> None:
        """Reinicia el conteo de deduplicacion y delega en Partida.nuevo_zapato()."""
        self._cartas_jugador_registradas = 0
        self._cartas_crupier_registradas = 0
        self.partida.nuevo_zapato()
