"""
Pruebas unitarias para el modelo de datos Capsule.
"""

import pytest
from models.capsule import Capsule


def test_capsule_initialization_and_defaults():
    cap = Capsule(
        title="Amor por la lectura",
        topic="Valores y Principios",
        content="Los libros nos abren ventanas a mundos que jamás imaginaríamos."
    )
    assert cap.title == "Amor por la lectura"
    assert cap.topic == "Valores y Principios"
    assert cap.is_approved is False
    assert cap.created_at is not None
    assert cap.updated_at is not None


def test_capsule_to_dict():
    cap = Capsule(
        id=1,
        title="Mi primera bicicleta",
        topic="Infancia y Familia",
        content="Una bicicleta roja que me regaló mi tío a los ocho años.",
        is_approved=True
    )
    d = cap.to_dict()
    assert d["id"] == 1
    assert d["title"] == "Mi primera bicicleta"
    assert d["is_approved"] is True

