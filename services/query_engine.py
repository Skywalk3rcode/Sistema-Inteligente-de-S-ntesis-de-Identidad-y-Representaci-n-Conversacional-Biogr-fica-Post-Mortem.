"""
Motor de consulta local para LegadoVivo basado estrictamente en fuentes autorizadas.
Aplica principios de fidelidad de datos, cita de fuentes y abstención deliberada
(sin IA generativa ni invención de hechos).
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from models.capsule import Capsule
from storage.repository import CapsuleRepository
from config import DISCLAIMER_TEXT, ABSTENTION_MESSAGE


@dataclass
class QueryResult:
    """Estructura estandarizada de respuesta para una consulta del legado."""
    query: str
    has_matches: bool
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    disclaimer: str = DISCLAIMER_TEXT
    total_approved_available: int = 0


class QueryEngine:
    """
    Motor determinista de recuperación sobre el archivo autorizado.
    Garantiza que toda respuesta se derive de fuentes explícitamente aprobadas.
    """

    # Palabras comunes vacías en español para mejorar la precisión léxica
    STOPWORDS = {
        "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del",
        "a", "al", "en", "con", "por", "para", "sobre", "entre", "hacia",
        "desde", "y", "o", "u", "e", "que", "que", "como", "cual", "quien",
        "se", "su", "sus", "mi", "mis", "tu", "tus", "es", "son", "fue",
        "era", "me", "te", "le", "nos", "les", "lo", "ya", "no", "si"
    }

    def __init__(self, repository: Optional[CapsuleRepository] = None):
        self.repository = repository or CapsuleRepository()

    def _normalize_text(self, text: str) -> str:
        """Normaliza cadenas eliminando puntuación y convirtiendo a minúsculas."""
        text = text.lower()
        # Reemplazar tildes comunes para búsqueda tolerante
        replacements = (
            ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ü", "u")
        )
        for orig, sub in replacements:
            text = text.replace(orig, sub)
        # Quitar signos de puntuación
        text = re.sub(r"[^\w\s]", " ", text)
        return text

    def _extract_tokens(self, text: str) -> List[str]:
        """Extrae términos relevantes excluyendo stopwords."""
        normalized = self._normalize_text(text)
        words = normalized.split()
        return [w for w in words if len(w) >= 3 and w not in self.STOPWORDS]

    def _calculate_relevance(self, query_tokens: List[str], raw_query: str, capsule: Capsule) -> float:
        """
        Calcula un puntaje de coincidencia ponderado para una cápsula:
        - Coincidencia exacta de frase: mayor peso.
        - Coincidencias en título: peso alto.
        - Coincidencias en tema: peso medio.
        - Coincidencias en contenido: peso base.
        """
        score = 0.0
        norm_title = self._normalize_text(capsule.title)
        norm_topic = self._normalize_text(capsule.topic)
        norm_content = self._normalize_text(capsule.content)
        norm_query = self._normalize_text(raw_query)

        # Bonificación por frase exacta contenida
        if len(norm_query) > 4:
            if norm_query in norm_title:
                score += 10.0
            if norm_query in norm_content:
                score += 6.0
            if norm_query in norm_topic:
                score += 5.0

        for token in query_tokens:
            if token in norm_title:
                score += 3.5
            if token in norm_topic:
                score += 2.5
            if token in norm_content:
                score += 1.2

        return score

    def query(self, raw_query: str) -> QueryResult:
        """
        Ejecuta la consulta sobre las cápsulas aprobadas.
        Si no hay términos o coincidencias suficientes, se abstiene formalmente.
        """
        clean_query = (raw_query or "").strip()
        approved_capsules = self.repository.get_all(approved_only=True)
        total_approved = len(approved_capsules)

        # Validación 1: Consulta vacía
        if not clean_query:
            return QueryResult(
                query=clean_query,
                has_matches=False,
                answer="Por favor, ingrese un tema, pregunta o palabra clave para consultar el legado.",
                sources=[],
                total_approved_available=total_approved
            )

        # Validación 2: No hay fuentes aprobadas en el sistema
        if total_approved == 0:
            return QueryResult(
                query=clean_query,
                has_matches=False,
                answer=(
                    "No es posible responder: actualmente no existe ninguna cápsula autorizada "
                    "como fuente en la biblioteca. Para consultar el legado, el titular debe "
                    "aprobar previamente al menos una cápsula temática."
                ),
                sources=[],
                total_approved_available=0
            )

        tokens = self._extract_tokens(clean_query)
        # Si la consulta consta solo de caracteres o palabras excluidas
        if not tokens:
            tokens = [self._normalize_text(clean_query)]

        # Evaluar relevancia para cada cápsula autorizada
        scored_capsules = []
        for cap in approved_capsules:
            score = self._calculate_relevance(tokens, clean_query, cap)
            if score > 0.0:
                scored_capsules.append((score, cap))

        # Validación 3: Abstención ante falta de coincidencias
        if not scored_capsules:
            return QueryResult(
                query=clean_query,
                has_matches=False,
                answer=ABSTENTION_MESSAGE,
                sources=[],
                total_approved_available=total_approved
            )

        # Ordenar por relevancia descendente y limitar a las fuentes más pertinentes
        scored_capsules.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_capsules[:3]

        sources_data = []
        answer_parts = [
            f"A partir de las fuentes autorizadas registradas por el titular, se recuperó "
            f"la siguiente información relacionada con '{clean_query}':\n"
        ]

        for idx, (score, cap) in enumerate(top_matches, start=1):
            # Citar textualmente el extracto
            excerpt = cap.content if len(cap.content) <= 220 else cap.content[:217] + "..."
            answer_parts.append(
                f"[{idx}] Tema: {cap.topic} — \"{cap.title}\"\n"
                f"    «{excerpt}»\n"
            )
            sources_data.append({
                "id": cap.id,
                "title": cap.title,
                "topic": cap.topic,
                "created_at": cap.created_at,
                "excerpt": excerpt
            })

        answer_parts.append(
            "Conclusión: La anterior información refleja textualmente los principios y recuerdos "
            "consignados en las fuentes citadas. Ninguna afirmación ha sido inventada."
        )

        full_answer = "\n".join(answer_parts)

        return QueryResult(
            query=clean_query,
            has_matches=True,
            answer=full_answer,
            sources=sources_data,
            total_approved_available=total_approved
        )

