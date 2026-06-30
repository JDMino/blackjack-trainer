"""
Configuracion compartida de pytest para todo el proyecto.

Fuerza a Qt a usar el plugin 'offscreen' (sin necesitar una pantalla
real) ANTES de que se importe PySide6 en cualquier test. Esto permite
correr toda la suite, incluyendo los tests de app/overlay/, en
cualquier maquina (incluido un servidor de CI sin entorno grafico).
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(scope="session")
def qapp():
    """
    QApplication unica para toda la sesion de tests. PySide6 no
    permite crear mas de una QApplication por proceso, por eso este
    fixture tiene scope='session': se crea una sola vez y se reutiliza
    en todos los tests que la necesiten.
    """
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app
