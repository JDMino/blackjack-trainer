"""
Motor de conteo: sistema Hi-Lo.

Reglas del Hi-Lo:
    - Cartas 2, 3, 4, 5, 6      -> +1  (cartas bajas, "buenas" para el jugador si quedan pocas)
    - Cartas 7, 8, 9            ->  0  (neutras)
    - Cartas 10, J, Q, K, A     -> -1  (cartas altas, favorecen al jugador si quedan muchas)

Esta clase NO sabe nada de vision, captura de pantalla ni overlay.
Solo recibe objetos Carta (uno por uno, a medida que se observan) y
mantiene el estado del conteo. Esto la hace facil de probar por
consola o con pytest, sin depender de ninguna otra parte del sistema.
"""

from __future__ import annotations

from app.models.carta import Carta

# Cuantas cartas tiene un mazo estandar (sin jokers).
CARTAS_POR_MAZO = 52


class ContadorHiLo:
    """Mantiene el estado del conteo Hi-Lo a lo largo de un zapato (shoe)."""

    def __init__(self, num_mazos: int = 6):
        """
        Args:
            num_mazos: cuantos mazos de 52 cartas conforman el zapato.
                       Los casinos suelen usar 6 u 8; se deja configurable
                       porque las reglas de la mesa pueden variar.
        """
        if num_mazos <= 0:
            raise ValueError("num_mazos debe ser mayor que 0")

        self.num_mazos = num_mazos
        self.running_count: int = 0
        self.cartas_vistas: int = 0

    def registrar_carta(self, carta: Carta) -> None:
        """
        Actualiza el running count con una carta recien observada.
        Debe llamarse exactamente una vez por cada carta que aparece
        en la mesa (jugador y crupier incluidos), tal como indica la
        regla de negocio del proyecto.
        """
        self.running_count += self._valor_conteo(carta)
        self.cartas_vistas += 1

    @staticmethod
    def _valor_conteo(carta: Carta) -> int:
        """Traduce una carta a su valor en el sistema Hi-Lo (+1, 0 o -1)."""
        if carta.rango in ("2", "3", "4", "5", "6"):
            return 1
        if carta.rango in ("7", "8", "9"):
            return 0
        # 10, J, Q, K, A
        return -1

    @property
    def cartas_totales_en_zapato(self) -> int:
        """Cuantas cartas hay en total al iniciar el zapato (sin descartar)."""
        return self.num_mazos * CARTAS_POR_MAZO

    @property
    def mazos_restantes(self) -> float:
        """
        Estimacion de cuantos mazos quedan por jugar, en base a las
        cartas ya vistas. Se evita devolver 0 o negativo para no
        dividir por cero al calcular el true count: como minimo se
        considera medio mazo restante.
        """
        cartas_restantes = self.cartas_totales_en_zapato - self.cartas_vistas
        mazos = cartas_restantes / CARTAS_POR_MAZO
        return max(mazos, 0.5)

    @property
    def true_count(self) -> float:
        """
        Running count ajustado por los mazos restantes. Es la metrica
        que realmente se usa para tomar decisiones de apuesta/estrategia,
        ya que un mismo running count significa cosas distintas segun
        cuantas cartas quedan por salir.
        """
        return self.running_count / self.mazos_restantes

    def reiniciar(self) -> None:
        """
        Reinicia el conteo para un nuevo mazo/zapato, segun la regla
        de negocio: el conteo debe reiniciarse cuando el usuario
        indique el comienzo de un nuevo mazo o zapato.
        """
        self.running_count = 0
        self.cartas_vistas = 0

    def __repr__(self) -> str:
        return (
            f"ContadorHiLo(running_count={self.running_count:+d}, "
            f"true_count={self.true_count:+.2f}, "
            f"cartas_vistas={self.cartas_vistas}, "
            f"mazos_restantes={self.mazos_restantes:.2f})"
        )
