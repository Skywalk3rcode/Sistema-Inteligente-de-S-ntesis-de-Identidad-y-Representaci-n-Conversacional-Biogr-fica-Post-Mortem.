"""
Modelo de datos para las cápsulas de memoria y valores de LegadoVivo.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Capsule:
    """
    Representa una cápsula temática de memoria, valor o vivencia.
    """
    id: Optional[int] = None
    title: str = ""
    topic: str = ""
    content: str = ""
    is_approved: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        # Asignar marcas temporales en formato ISO si no fueron provistas
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.created_at is None:
            self.created_at = now_iso
        if self.updated_at is None:
            self.updated_at = now_iso

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la cápsula en un diccionario."""
        return asdict(self)

    @classmethod
    def from_row(cls, row: tuple) -> "Capsule":
        """
        Construye una instancia a partir de una fila devuelta por SQLite:
        (id, title, topic, content, is_approved, created_at, updated_at)
        """
        return cls(
            id=row[0],
            title=row[1],
            topic=row[2],
            content=row[3],
            is_approved=bool(row[4]),
            created_at=row[5],
            updated_at=row[6]
        )

