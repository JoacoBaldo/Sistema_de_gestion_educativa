# test_error.py
import os  # Importación no utilizada (Ruff debería fallar)


def suma(a: int, b: int) -> int:
    return "no soy un entero"  # Error de tipo (MyPy debería fallar)


def test_suma():
    assert False  # Prueba fallida (Pytest debería fallar)
