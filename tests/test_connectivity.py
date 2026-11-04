"""
Pruebas para ConnectivityService: monitoreo y simulación offline.
"""

from services.connectivity_service import ConnectivityService
from config import OFFLINE_NOTICE


def test_connectivity_default_and_simulation():
    svc = ConnectivityService()

    # Por defecto no está simulado
    assert svc.is_simulated_offline is False

    # Activar simulación offline
    svc.set_simulated_offline(True)
    assert svc.is_simulated_offline is True
    assert svc.is_connected() is False

    summary = svc.get_status_summary()
    assert summary["is_connected"] is False
    assert summary["is_simulated"] is True
    assert "fuera de línea" in summary["sync_note"].lower()
    assert summary["offline_notice"] == OFFLINE_NOTICE

    # Alternar simulación nuevamente
    new_state = svc.toggle_simulation()
    assert new_state is False
    assert svc.is_simulated_offline is False

