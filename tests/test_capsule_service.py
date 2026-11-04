"""
Pruebas para CapsuleService y validación de reglas de negocio.
"""

import os
import tempfile
import pytest
from storage.repository import CapsuleRepository
from services.capsule_service import CapsuleService


@pytest.fixture
def service():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    repo = CapsuleRepository(db_path=path)
    svc = CapsuleService(repository=repo)
    yield svc
    if os.path.exists(path):
        os.remove(path)


def test_validation_mandatory_fields(service):
    # Título vacío
    ok, msg, cap = service.create_capsule("", "Valores y Principios", "Contenido largo válido")
    assert ok is False
    assert "título es obligatorio" in msg.lower()

    # Título demasiado corto
    ok, msg, cap = service.create_capsule("ab", "Valores y Principios", "Contenido largo válido")
    assert ok is False
    assert "al menos 3 caracteres" in msg.lower()

    # Tema vacío
    ok, msg, cap = service.create_capsule("Título Válido", "", "Contenido largo válido")
    assert ok is False
    assert "tema o categoría" in msg.lower()

    # Contenido vacío
    ok, msg, cap = service.create_capsule("Título Válido", "Valores y Principios", "")
    assert ok is False
    assert "contenido" in msg.lower()

    # Contenido menor a 10 caracteres
    ok, msg, cap = service.create_capsule("Título Válido", "Valores y Principios", "Corto")
    assert ok is False
    assert "al menos 10 caracteres" in msg.lower()


def test_create_and_toggle_approval(service):
    ok, msg, cap = service.create_capsule(
        title="Consejo de honestidad",
        topic="Valores y Principios",
        content="La verdad debe prevalecer siempre en las decisiones cotidianas.",
        is_approved=False
    )
    assert ok is True
    assert cap is not None
    assert cap.is_approved is False

    # Alternar aprobación a True
    success, t_msg, new_state = service.toggle_approval(cap.id)
    assert success is True
    assert new_state is True
    assert service.get_capsule(cap.id).is_approved is True

    # Alternar aprobación a False (revocar)
    success, t_msg, new_state = service.toggle_approval(cap.id)
    assert success is True
    assert new_state is False
    assert service.get_capsule(cap.id).is_approved is False


def test_delete_capsule(service):
    ok, _, cap = service.create_capsule(
        title="Cápsula Efímera",
        topic="Anécdotas y Consejos",
        content="Esta cápsula será eliminada para validar la operación de borrado."
    )
    assert service.get_capsule(cap.id) is not None

    del_ok, del_msg = service.delete_capsule(cap.id)
    assert del_ok is True
    assert service.get_capsule(cap.id) is None

