"""
Pruebas de persistencia local SQLite para CapsuleRepository.
"""

import os
import tempfile
import pytest
from models.capsule import Capsule
from storage.repository import CapsuleRepository


@pytest.fixture
def temp_repo():
    """Crea un repositorio respaldado por una base de datos temporal."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    repo = CapsuleRepository(db_path=path)
    yield repo
    if os.path.exists(path):
        os.remove(path)


def test_create_and_retrieve_capsule(temp_repo):
    cap = Capsule(
        title="Constancia en los estudios",
        topic="Trabajo y Carrera",
        content="Estudiar a diario forja el carácter y la inteligencia técnica.",
        is_approved=False
    )
    saved = temp_repo.create(cap)
    assert saved.id is not None
    assert saved.id > 0

    retrieved = temp_repo.get_by_id(saved.id)
    assert retrieved is not None
    assert retrieved.title == "Constancia en los estudios"
    assert retrieved.is_approved is False


def test_update_capsule(temp_repo):
    cap = Capsule(
        title="Título Inicial",
        topic="Filosofía de Vida",
        content="Contenido original de la cápsula de prueba.",
        is_approved=False
    )
    saved = temp_repo.create(cap)

    saved.title = "Título Modificado"
    saved.content = "Contenido enriquecido con nuevos recuerdos."
    saved.is_approved = True
    success = temp_repo.update(saved)
    assert success is True

    updated = temp_repo.get_by_id(saved.id)
    assert updated.title == "Título Modificado"
    assert updated.is_approved is True
    assert updated.content == "Contenido enriquecido con nuevos recuerdos."


def test_set_approval(temp_repo):
    cap = Capsule(
        title="Cápsula para Autorizar",
        topic="Valores y Principios",
        content="Contenido que será aprobado para consulta del legado.",
        is_approved=False
    )
    saved = temp_repo.create(cap)
    assert saved.is_approved is False

    # Aprobar
    temp_repo.set_approval(saved.id, True)
    assert temp_repo.get_by_id(saved.id).is_approved is True

    # Revocar aprobación
    temp_repo.set_approval(saved.id, False)
    assert temp_repo.get_by_id(saved.id).is_approved is False


def test_delete_capsule(temp_repo):
    cap = Capsule(
        title="Para borrar",
        topic="Anécdotas y Consejos",
        content="Este registro será eliminado en la prueba.",
        is_approved=False
    )
    saved = temp_repo.create(cap)
    assert temp_repo.count() == 1

    deleted = temp_repo.delete(saved.id)
    assert deleted is True
    assert temp_repo.count() == 0
    assert temp_repo.get_by_id(saved.id) is None


def test_persistence_across_reopen():
    """Verifica que los datos persisten al cerrar y reabrir la base de datos."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Sesión 1: Crear datos
    repo1 = CapsuleRepository(db_path=path)
    cap = Capsule(
        title="Persistencia comprobada",
        topic="Valores y Principios",
        content="Este contenido debe sobrevivir al cierre y reinicio de la app.",
        is_approved=True
    )
    saved = repo1.create(cap)
    del repo1  # Cierra explícitamente

    # Sesión 2: Reabrir repositorio con el mismo archivo físico
    repo2 = CapsuleRepository(db_path=path)
    recovered = repo2.get_by_id(saved.id)
    assert recovered is not None
    assert recovered.title == "Persistencia comprobada"
    assert recovered.is_approved is True

    if os.path.exists(path):
        os.remove(path)


def test_seed_initial_data(temp_repo):
    assert temp_repo.count() == 0
    temp_repo.seed_initial_data()
    assert temp_repo.count() == 4
    # Verificar que las autorizadas se filtran adecuadamente
    approved = temp_repo.get_all(approved_only=True)
    assert len(approved) == 3

