"""
Servicio de gestión de fotografías de legado para LegadoVivo.
Abstrae la captura de imágenes entre plataformas:
  - Android: usa plyer.camera para abrir la cámara nativa.
  - Escritorio: usa plyer.filechooser como fallback de desarrollo.
Las fotos se copian al directorio privado de la aplicación para asegurar
que permanezcan disponibles con independencia del almacenamiento externo.
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Callable, Optional

from kivy.utils import platform


def _get_photos_dir() -> Path:
    """
    Determina el directorio privado donde se almacenan las fotos de legado.
    Se ubica dentro del user_data_dir de la aplicación Kivy, que en Android
    corresponde al almacenamiento privado de la app (no requiere permisos de galería
    en Android 10+).
    """
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and hasattr(app, "user_data_dir") and app.user_data_dir:
            base = Path(app.user_data_dir)
        else:
            base = Path(__file__).resolve().parent.parent
    except Exception:
        base = Path(__file__).resolve().parent.parent

    photos_dir = base / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)
    return photos_dir


def copy_to_storage(source_path: str) -> Optional[str]:
    """
    Copia una imagen desde su ubicación temporal o de galería al directorio
    privado de la aplicación. Devuelve la ruta definitiva o None si falla.
    """
    if not source_path or not os.path.isfile(source_path):
        return None

    try:
        photos_dir = _get_photos_dir()
        # Nombre único para evitar colisiones entre cápsulas
        ext = Path(source_path).suffix.lower() or ".jpg"
        dest_name = f"capsule_photo_{uuid.uuid4().hex}{ext}"
        dest_path = photos_dir / dest_name
        shutil.copy2(source_path, dest_path)
        return str(dest_path)
    except Exception as e:
        print(f"[PhotoService] Error al copiar foto: {e}")
        return None


def delete_photo(photo_path: Optional[str]) -> None:
    """
    Elimina el archivo de foto del almacenamiento si existe.
    Se llama al borrar una cápsula que tenía foto adjunta.
    """
    if not photo_path:
        return
    try:
        path = Path(photo_path)
        if path.is_file():
            path.unlink()
    except Exception as e:
        print(f"[PhotoService] Error al eliminar foto: {e}")


def capture_photo(on_complete: Callable[[Optional[str]], None]) -> None:
    """
    Inicia el proceso de captura o selección de imagen según la plataforma:
      - Android: abre la cámara nativa via plyer.camera.
      - iOS:     usa plyer.camera si está disponible.
      - Otros:   abre el selector de archivos via plyer.filechooser (fallback escritorio).

    Parámetro:
        on_complete(path): callback que recibe la ruta definitiva del archivo
                           almacenado en el directorio privado, o None si se canceló.
    """
    if platform in ("android", "ios"):
        _capture_with_camera(on_complete)
    else:
        _select_with_filechooser(on_complete)


def _capture_with_camera(on_complete: Callable[[Optional[str]], None]) -> None:
    """Captura con la cámara nativa del dispositivo (Android/iOS)."""
    try:
        from plyer import camera
        photos_dir = _get_photos_dir()
        # Ruta temporal donde plyer guardará la foto recién tomada
        temp_path = str(photos_dir / f"temp_capture_{uuid.uuid4().hex}.jpg")

        def _on_camera_complete(filename: str) -> None:
            """Callback de plyer.camera: recibe la ruta del archivo tomado."""
            if filename and os.path.isfile(filename):
                final_path = copy_to_storage(filename)
                # Limpiar el temporal si es diferente al destino
                if filename != final_path:
                    try:
                        os.remove(filename)
                    except Exception:
                        pass
                on_complete(final_path)
            else:
                on_complete(None)

        camera.take_picture(filename=temp_path, on_complete=_on_camera_complete)

    except NotImplementedError:
        # plyer.camera no implementado en esta plataforma; usar fallback
        print("[PhotoService] plyer.camera no disponible; usando filechooser.")
        _select_with_filechooser(on_complete)
    except Exception as e:
        print(f"[PhotoService] Error al abrir cámara: {e}")
        on_complete(None)


def _select_with_filechooser(on_complete: Callable[[Optional[str]], None]) -> None:
    """Selector de archivos de imagen (fallback para escritorio)."""
    try:
        from plyer import filechooser

        def _on_selection(selection):
            if selection and len(selection) > 0:
                chosen = selection[0]
                final_path = copy_to_storage(chosen)
                on_complete(final_path)
            else:
                on_complete(None)

        filechooser.open_file(
            title="Seleccionar fotografía de legado",
            filters=[["Imágenes", "*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]],
            on_selection=_on_selection
        )

    except Exception as e:
        print(f"[PhotoService] Error al abrir selector de archivos: {e}")
        on_complete(None)
