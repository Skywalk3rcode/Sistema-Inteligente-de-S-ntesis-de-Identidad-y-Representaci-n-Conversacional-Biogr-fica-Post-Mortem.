"""
Prueba de integración rápida para la interfaz de usuario móvil de LegadoVivo.
Verifica que la jerarquía de widgets, pantallas y layout principal se construyen sin fallos.
"""

import os
import tempfile
import pytest

# Configurar Kivy en modo sin entrada interactiva
os.environ["KIVY_NO_ARGS"] = "1"

from storage.repository import CapsuleRepository
from services.capsule_service import CapsuleService
from services.query_engine import QueryEngine
from services.connectivity_service import ConnectivityService
from ui.app_ui import MainMobileLayout


@pytest.fixture
def app_components():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    repo = CapsuleRepository(db_path=path)
    repo.seed_initial_data()
    svc = CapsuleService(repository=repo)
    engine = QueryEngine(repository=repo)
    conn = ConnectivityService()

    yield repo, svc, engine, conn

    if os.path.exists(path):
        os.remove(path)


def test_main_layout_construction(app_components):
    repo, svc, engine, conn = app_components
    layout = MainMobileLayout(
        capsule_service=svc,
        query_engine=engine,
        connectivity_service=conn
    )

    assert layout is not None
    assert layout.sm is not None
    assert layout.sm.has_screen("library")
    assert layout.sm.has_screen("form")
    assert layout.sm.has_screen("query")


def test_screen_navigation(app_components):
    repo, svc, engine, conn = app_components
    layout = MainMobileLayout(
        capsule_service=svc,
        query_engine=engine,
        connectivity_service=conn
    )

    # Navegar a formulario
    layout.navigate_to_form(None)
    assert layout.sm.current == "form"

    # Navegar a consulta
    layout.navigate_to_query()
    assert layout.sm.current == "query"

    # Volver a biblioteca
    layout.navigate_to_library()
    assert layout.sm.current == "library"

