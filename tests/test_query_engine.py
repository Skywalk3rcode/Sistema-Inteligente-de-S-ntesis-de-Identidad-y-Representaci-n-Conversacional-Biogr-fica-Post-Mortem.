"""
Pruebas para el motor de consulta QueryEngine: fidelidad, citación de fuentes y abstención estricta.
"""

import os
import tempfile
import pytest
from storage.repository import CapsuleRepository
from models.capsule import Capsule
from services.query_engine import QueryEngine
from config import ABSTENTION_MESSAGE, DISCLAIMER_TEXT


@pytest.fixture
def query_setup():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    repo = CapsuleRepository(db_path=path)

    # 1. Cápsula Aprobada A
    repo.create(Capsule(
        title="La honestidad en el trabajo",
        topic="Valores y Principios",
        content="La palabra empeñada y el respeto en los negocios valen más que el oro.",
        is_approved=True
    ))

    # 2. Cápsula Aprobada B
    repo.create(Capsule(
        title="El café en las mañanas familiares",
        topic="Infancia y Familia",
        content="Compartir una taza de café caliente en el patio nos enseñó unión y diálogo.",
        is_approved=True
    ))

    # 3. Cápsula NO Aprobada (Borrador Privado) C
    repo.create(Capsule(
        title="Secretos de inversiones financieras",
        topic="Filosofía de Vida",
        content="Comprar acciones de tecnología y diversificar en bienes raíces.",
        is_approved=False
    ))

    engine = QueryEngine(repository=repo)
    yield engine, repo

    if os.path.exists(path):
        os.remove(path)


def test_query_returns_approved_source_with_citation(query_setup):
    engine, _ = query_setup
    result = engine.query("honestidad y trabajo")

    assert result.has_matches is True
    assert len(result.sources) > 0
    assert result.sources[0]["title"] == "La honestidad en el trabajo"
    assert "palabra empeñada" in result.answer
    assert result.disclaimer == DISCLAIMER_TEXT


def test_query_strictly_excludes_unapproved_capsules(query_setup):
    engine, _ = query_setup
    # Búsqueda de tema presente en la cápsula privada no autorizada
    result = engine.query("inversiones financieras y bienes raíces")

    # Debe abstenerse porque la cápsula existe pero NO está aprobada
    assert result.has_matches is False
    assert len(result.sources) == 0
    assert result.answer == ABSTENTION_MESSAGE


def test_query_abstention_on_unrelated_topic(query_setup):
    engine, _ = query_setup
    # Tema completamente ajeno
    result = engine.query("física cuántica y viajes espaciales a Marte")

    assert result.has_matches is False
    assert len(result.sources) == 0
    assert result.answer == ABSTENTION_MESSAGE


def test_query_empty_prompt(query_setup):
    engine, _ = query_setup
    result = engine.query("   ")
    assert result.has_matches is False
    assert "ingrese un tema" in result.answer.lower()

