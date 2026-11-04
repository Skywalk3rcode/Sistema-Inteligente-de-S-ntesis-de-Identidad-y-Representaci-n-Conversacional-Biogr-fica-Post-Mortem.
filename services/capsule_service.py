"""
Capa de lógica de negocio para la gestión de cápsulas en LegadoVivo.
Aplica validaciones estrictas, reglas de integridad y gestión de estados de aprobación.
"""

from typing import Tuple, Optional, List
from datetime import datetime
from models.capsule import Capsule
from storage.repository import CapsuleRepository


class CapsuleService:
    """
    Servicio encargado de la lógica operativa y validación de cápsulas.
    """

    def __init__(self, repository: Optional[CapsuleRepository] = None):
        self.repository = repository or CapsuleRepository()

    def validate_fields(self, title: str, topic: str, content: str) -> Tuple[bool, str]:
        """
        Valida que los campos obligatorios cumplan con las restricciones de negocio.
        Retorna (True, "") si es válido, o (False, mensaje_error) si falla.
        """
        clean_title = (title or "").strip()
        clean_topic = (topic or "").strip()
        clean_content = (content or "").strip()

        if not clean_title:
            return False, "El título es obligatorio y no puede contener solo espacios."

        if len(clean_title) < 3:
            return False, f"El título debe tener al menos 3 caracteres (actual: {len(clean_title)})."

        if len(clean_title) > 120:
            return False, f"El título excede el límite máximo de 120 caracteres (actual: {len(clean_title)})."

        if not clean_topic:
            return False, "Debe seleccionar un tema o categoría para la cápsula."

        if not clean_content:
            return False, "El contenido del recuerdo o valor no puede estar vacío."

        if len(clean_content) < 10:
            return False, f"El contenido debe tener al menos 10 caracteres (actual: {len(clean_content)})."

        return True, ""

    def create_capsule(
        self,
        title: str,
        topic: str,
        content: str,
        is_approved: bool = False
    ) -> Tuple[bool, str, Optional[Capsule]]:
        """
        Valida y almacena una nueva cápsula.
        """
        is_valid, error_msg = self.validate_fields(title, topic, content)
        if not is_valid:
            return False, error_msg, None

        capsule = Capsule(
            title=title.strip(),
            topic=topic.strip(),
            content=content.strip(),
            is_approved=is_approved
        )

        try:
            saved_capsule = self.repository.create(capsule)
            return True, "Cápsula registrada con éxito.", saved_capsule
        except Exception as e:
            return False, f"Error de almacenamiento local: {str(e)}", None

    def update_capsule(
        self,
        capsule_id: int,
        title: str,
        topic: str,
        content: str,
        is_approved: bool
    ) -> Tuple[bool, str, Optional[Capsule]]:
        """
        Valida y actualiza los datos de una cápsula existente.
        """
        is_valid, error_msg = self.validate_fields(title, topic, content)
        if not is_valid:
            return False, error_msg, None

        existing = self.repository.get_by_id(capsule_id)
        if not existing:
            return False, f"No se encontró la cápsula con ID {capsule_id}.", None

        existing.title = title.strip()
        existing.topic = topic.strip()
        existing.content = content.strip()
        existing.is_approved = is_approved
        existing.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            success = self.repository.update(existing)
            if success:
                return True, "Cápsula actualizada correctamente.", existing
            return False, "No se pudo actualizar el registro.", None
        except Exception as e:
            return False, f"Error al actualizar: {str(e)}", None

    def toggle_approval(self, capsule_id: int) -> Tuple[bool, str, bool]:
        """
        Alterna el estado de aprobación de una cápsula para uso como fuente.
        Retorna: (éxito, mensaje, nuevo_estado)
        """
        capsule = self.repository.get_by_id(capsule_id)
        if not capsule:
            return False, f"Cápsula {capsule_id} no encontrada.", False

        new_status = not capsule.is_approved
        success = self.repository.set_approval(capsule_id, new_status)
        if success:
            msg = (
                "Cápsula autorizada como fuente para consultas del legado."
                if new_status
                else "Autorización retirada. La cápsula permanecerá solo en archivo privado."
            )
            return True, msg, new_status
        return False, "Error al modificar la autorización.", capsule.is_approved

    def delete_capsule(self, capsule_id: int) -> Tuple[bool, str]:
        """
        Elimina de forma permanente una cápsula.
        """
        capsule = self.repository.get_by_id(capsule_id)
        if not capsule:
            return False, f"La cápsula con ID {capsule_id} no existe."

        try:
            success = self.repository.delete(capsule_id)
            if success:
                return True, f"Cápsula '{capsule.title}' eliminada exitosamente."
            return False, "No se pudo completar la eliminación."
        except Exception as e:
            return False, f"Error al eliminar registro: {str(e)}"

    def get_capsule(self, capsule_id: int) -> Optional[Capsule]:
        """Recupera una cápsula individual."""
        return self.repository.get_by_id(capsule_id)

    def list_capsules(self, topic: Optional[str] = None, approved_only: bool = False) -> List[Capsule]:
        """Lista las cápsulas registradas según los filtros especificados."""
        return self.repository.get_all(topic=topic, approved_only=approved_only)

