"""
Capa de persistencia local utilizando SQLite para LegadoVivo.
Proporciona almacenamiento no volátil, ACID y completamente desacoplado de la red.
"""

import sqlite3
from typing import List, Optional
from models.capsule import Capsule
from config import get_database_path


class CapsuleRepository:
    """
    Repositorio de acceso a datos para la entidad Cápsula.
    Gestiona la inicialización de esquemas, transacciones y consultas.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_database_path()
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión configurada hacia la base de datos SQLite."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self) -> None:
        """Inicializa la tabla e índices si no existen."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS capsules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    is_approved INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_capsules_approved 
                ON capsules (is_approved)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_capsules_topic 
                ON capsules (topic)
            """)
            conn.commit()
        finally:
            conn.close()

    def create(self, capsule: Capsule) -> Capsule:
        """Inserta una nueva cápsula y actualiza su identificador generado."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO capsules (title, topic, content, is_approved, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                capsule.title,
                capsule.topic,
                capsule.content,
                1 if capsule.is_approved else 0,
                capsule.created_at,
                capsule.updated_at
            ))
            capsule.id = cursor.lastrowid
            conn.commit()
            return capsule
        finally:
            conn.close()

    def update(self, capsule: Capsule) -> bool:
        """Actualiza los campos de una cápsula existente."""
        if capsule.id is None:
            return False

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE capsules
                SET title = ?, topic = ?, content = ?, is_approved = ?, updated_at = ?
                WHERE id = ?
            """, (
                capsule.title,
                capsule.topic,
                capsule.content,
                1 if capsule.is_approved else 0,
                capsule.updated_at,
                capsule.id
            ))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_by_id(self, capsule_id: int) -> Optional[Capsule]:
        """Recupera una cápsula por su identificador único."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM capsules WHERE id = ?", (capsule_id,))
            row = cursor.fetchone()
            if row:
                return Capsule(
                    id=row["id"],
                    title=row["title"],
                    topic=row["topic"],
                    content=row["content"],
                    is_approved=bool(row["is_approved"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
            return None
        finally:
            conn.close()

    def get_all(self, topic: Optional[str] = None, approved_only: bool = False) -> List[Capsule]:
        """
        Lista cápsulas almacenadas con opción de filtrado por tema o estado de aprobación.
        """
        query = "SELECT * FROM capsules WHERE 1=1"
        params = []

        if topic and topic.strip():
            query += " AND topic = ?"
            params.append(topic.strip())

        if approved_only:
            query += " AND is_approved = 1"

        query += " ORDER BY id DESC"

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [
                Capsule(
                    id=row["id"],
                    title=row["title"],
                    topic=row["topic"],
                    content=row["content"],
                    is_approved=bool(row["is_approved"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                for row in rows
            ]
        finally:
            conn.close()

    def set_approval(self, capsule_id: int, is_approved: bool) -> bool:
        """
        Modifica el estado de aprobación de una cápsula como fuente autorizada.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE capsules 
                SET is_approved = ?, updated_at = datetime('now', 'localtime')
                WHERE id = ?
            """, (1 if is_approved else 0, capsule_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, capsule_id: int) -> bool:
        """Elimina permanentemente una cápsula de la base de datos."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM capsules WHERE id = ?", (capsule_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def count(self, approved_only: bool = False) -> int:
        """Devuelve el total de cápsulas registradas."""
        query = "SELECT COUNT(*) FROM capsules"
        params = []
        if approved_only:
            query += " WHERE is_approved = 1"

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def seed_initial_data(self) -> None:
        """
        Siembra datos ficticios de demostración si la base de datos está vacía.
        Cumple con el requisito de no emplear memorias personales reales.
        """
        if self.count() > 0:
            return

        sample_capsules = [
            Capsule(
                title="La honestidad en el trabajo y la palabra",
                topic="Valores y Principios",
                content=(
                    "Siempre creí que la palabra dada vale más que cualquier documento firmado. "
                    "En los negocios familiares, cuando cometíamos un error, lo reconocíamos "
                    "inmediatamente y asumíamos el costo. La confianza de las personas tarda años "
                    "en ganarse y solo un segundo en destruirse."
                ),
                is_approved=True
            ),
            Capsule(
                title="El valor del estudio y la perseverancia",
                topic="Trabajo y Carrera",
                content=(
                    "Mi primer empleo fue como aprendiz de taller. Me levantaba temprano a estudiar "
                    "antes de comenzar la jornada. Nunca te desanimes ante un problema complejo: "
                    "divídelo en partes pequeñas y resuélvelas con paciencia y método riguroso."
                ),
                is_approved=True
            ),
            Capsule(
                title="Tardes de café y unión familiar",
                topic="Infancia y Familia",
                content=(
                    "En la casa de campo, los domingos nos reuníamos en el patio a compartir café "
                    "y conversar. Esos momentos sencillos de escuchar a los mayores nos enseñaron "
                    "que el tiempo en familia es el patrimonio más valioso que dejamos."
                ),
                is_approved=True
            ),
            Capsule(
                title="Borrador confidencial de finanzas personales",
                topic="Filosofía de Vida",
                content=(
                    "Notas preliminares sobre presupuestos de ahorro y planes a largo plazo. "
                    "Este registro está incompleto y permanece como borrador estrictamente "
                    "privado, sin autorización para ser consultado como fuente del legado."
                ),
                is_approved=False
            )
        ]

        for cap in sample_capsules:
            self.create(cap)
