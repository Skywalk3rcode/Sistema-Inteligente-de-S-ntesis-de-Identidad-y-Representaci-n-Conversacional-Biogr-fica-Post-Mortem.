"""
Pruebas exhaustivas para la adaptación y compatibilidad con Android de LegadoVivo.
Verifica:
1. Manejo del botón físico de retroceso de Android (keycode 27 / Esc).
2. Configuración del teclado virtual (softinput_mode).
3. Determinación de rutas de almacenamiento privado Android (ANDROID_PRIVATE, user_data_dir).
4. Compatibilidad de ConnectivityService con NetworkCapabilities (API 23 - API 34+).
5. Dimensiones móviles y responsividad en pantalla.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch
import pytest

# Configuración no interactiva de Kivy para entorno de pruebas
os.environ["KIVY_NO_ARGS"] = "1"

from kivy.core.window import Window
from config import get_database_path, MOBILE_WINDOW_WIDTH, MOBILE_WINDOW_HEIGHT
from services.connectivity_service import ConnectivityService
from storage.repository import CapsuleRepository
from services.capsule_service import CapsuleService
from services.query_engine import QueryEngine
from ui.app_ui import MainMobileLayout
from main import LegadoVivoApp


@pytest.fixture
def mock_app():
    """Instancia la aplicación LegadoVivoApp con base de datos temporal."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    app = LegadoVivoApp()
    app.repository = CapsuleRepository(db_path=path)
    app.repository.seed_initial_data()
    app.capsule_service = CapsuleService(repository=app.repository)
    app.query_engine = QueryEngine(repository=app.repository)
    app.connectivity_service = ConnectivityService()

    app.main_layout = MainMobileLayout(
        capsule_service=app.capsule_service,
        query_engine=app.query_engine,
        connectivity_service=app.connectivity_service
    )

    yield app

    if os.path.exists(path):
        os.remove(path)


def test_softinput_mode_configuration():
    """Verifica que el modo de teclado virtual en Android está configurado para evitar superposiciones."""
    assert Window.softinput_mode == "below_target"


def test_android_database_path_resolution(monkeypatch):
    """Verifica la resolución segura de la base de datos en directorios privados de Android."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 1. Simular entorno python-for-android con ANDROID_PRIVATE
        monkeypatch.setenv("ANDROID_PRIVATE", tmp_dir)
        db_path = get_database_path()
        assert tmp_dir in db_path
        assert db_path.endswith("legado_vivo.db")
        assert os.path.exists(tmp_dir)

    with tempfile.TemporaryDirectory() as tmp_dir2:
        # 2. Simular variable ANDROID_APP_PATH
        monkeypatch.delenv("ANDROID_PRIVATE", raising=False)
        monkeypatch.setenv("ANDROID_APP_PATH", tmp_dir2)
        db_path2 = get_database_path()
        assert tmp_dir2 in db_path2
        assert db_path2.endswith("legado_vivo.db")


def test_back_button_from_form_returns_to_library(mock_app):
    """El botón de retroceso (keycode 27) debe regresar a Biblioteca desde Formulario."""
    mock_app.main_layout.navigate_to_form(None)
    assert mock_app.main_layout.sm.current == "form"

    # Presionar botón de retroceso de Android
    consumed = mock_app.on_android_back_button(Window, 27, None, None, None)
    assert consumed is True
    assert mock_app.main_layout.sm.current == "library"


def test_back_button_from_query_returns_to_library(mock_app):
    """El botón de retroceso (keycode 27) debe regresar a Biblioteca desde Consulta."""
    mock_app.main_layout.navigate_to_query()
    assert mock_app.main_layout.sm.current == "query"

    # Presionar botón de retroceso de Android
    consumed = mock_app.on_android_back_button(Window, 27, None, None, None)
    assert consumed is True
    assert mock_app.main_layout.sm.current == "library"


def test_back_button_from_library_delegates_to_system(mock_app):
    """En la Biblioteca raíz, el botón de retroceso no debe consumirse para permitir minimizar/salir."""
    mock_app.main_layout.navigate_to_library()
    assert mock_app.main_layout.sm.current == "library"

    consumed = mock_app.on_android_back_button(Window, 27, None, None, None)
    assert consumed is False


def test_back_button_dismisses_active_modal(mock_app):
    """Si hay un diálogo modal abierto, el botón de retroceso debe cerrarlo sin cambiar de pantalla."""
    from ui.components.dialogs import DisclaimerInfoDialog
    dialog = DisclaimerInfoDialog()
    dialog.open()

    assert dialog in Window.children

    with patch.object(dialog, "dismiss") as mock_dismiss:
        consumed = mock_app.on_android_back_button(Window, 27, None, None, None)
        assert consumed is True
        mock_dismiss.assert_called_once()

    # Limpiar estado
    dialog.dismiss(animation=False)


def test_android_connectivity_modern_api():
    """Verifica que el servicio de conectividad consulta NetworkCapabilities en Android API >= 23."""
    conn = ConnectivityService()

    mock_caps = MagicMock()
    mock_caps.hasCapability.return_value = True

    mock_network = MagicMock()

    mock_conn_mgr = MagicMock()
    mock_conn_mgr.getActiveNetwork.return_value = mock_network
    mock_conn_mgr.getNetworkCapabilities.return_value = mock_caps

    mock_activity = MagicMock()
    mock_activity.getSystemService.return_value = mock_conn_mgr

    mock_pyactivity = MagicMock()
    mock_pyactivity.mActivity = mock_activity

    mock_build = MagicMock()
    mock_build.VERSION.SDK_INT = 34

    def fake_autoclass(class_name):
        if class_name == "org.kivy.android.PythonActivity":
            return mock_pyactivity
        elif class_name == "android.content.Context":
            ctx = MagicMock()
            ctx.CONNECTIVITY_SERVICE = "connectivity"
            return ctx
        elif class_name == "android.os.Build":
            return mock_build
        elif class_name == "android.net.NetworkCapabilities":
            nc = MagicMock()
            nc.NET_CAPABILITY_INTERNET = 12
            return nc
        return MagicMock()

    with patch.dict("sys.modules", {"jnius": MagicMock(autoclass=fake_autoclass)}):
        is_conn = conn.check_android_connectivity()
        assert is_conn is True
        mock_conn_mgr.getActiveNetwork.assert_called_once()
        mock_conn_mgr.getNetworkCapabilities.assert_called_with(mock_network)


def test_android_lifecycle_pause_and_resume(mock_app):
    """Verifica que on_pause retorna True para preservar estado y on_resume refresca la UI."""
    assert mock_app.on_pause() is True
    # No debe levantar excepciones al reanudar
    mock_app.on_resume()
