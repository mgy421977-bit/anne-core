"""SQLite-backed persistent cognitive memory."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from anne_core.memory.models import CognitiveStructure
from anne_core.memory.semantic import LightweightSemanticMatcher


class CognitiveMemory:
    """Persistent cognitive memory with an explicit retrieval boundary."""

    def __init__(
        self,
        db_path: str | None = None,
        semantic_threshold: float = 0.42,
    ) -> None:
        if db_path is None:
            db_path = os.environ.get("ANNE_MEMORY_PATH", "anne_memory.db")
        self.db_path = str(Path(db_path).resolve())
        self.semantic_matcher = LightweightSemanticMatcher(semantic_threshold)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cognitive_structures (
                    id TEXT PRIMARY KEY,
                    concept TEXT,
                    question TEXT,
                    findings TEXT,
                    sources TEXT,
                    agreement TEXT,
                    contradictions TEXT,
                    confidence REAL,
                    evidence TEXT,
                    structure TEXT,
                    timestamp TEXT,
                    provenance TEXT,
                    reusable INTEGER,
                    tags TEXT,
                    raw_json TEXT
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_concept ON cognitive_structures(concept)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_question ON cognitive_structures(question)")
            conn.commit()

    def store(self, structure: CognitiveStructure) -> str:
        """Persist a CognitiveStructure. Returns its id."""
        data = structure.to_dict()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cognitive_structures (
                    id, concept, question, findings, sources, agreement,
                    contradictions, confidence, evidence, structure,
                    timestamp, provenance, reusable, tags, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    structure.id,
                    structure.concept,
                    structure.question,
                    json.dumps(structure.findings, ensure_ascii=False),
                    json.dumps(structure.sources, ensure_ascii=False),
                    json.dumps(structure.agreement, ensure_ascii=False),
                    json.dumps(structure.contradictions, ensure_ascii=False),
                    structure.confidence,
                    json.dumps(structure.evidence, ensure_ascii=False),
                    json.dumps(structure.structure, ensure_ascii=False),
                    structure.timestamp,
                    json.dumps(structure.provenance, ensure_ascii=False),
                    1 if structure.reusable else 0,
                    json.dumps(structure.tags, ensure_ascii=False),
                    json.dumps(data, ensure_ascii=False),
                ),
            )
            conn.commit()
        return structure.id

    def get(self, structure_id: str) -> CognitiveStructure | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT raw_json FROM cognitive_structures WHERE id = ?",
                (structure_id,),
            ).fetchone()
        if not row:
            return None
        return CognitiveStructure.from_dict(json.loads(row["raw_json"]))

    def search(
        self,
        query: str,
        limit: int = 5,
        min_confidence: float = 0.0,
    ) -> list[CognitiveStructure]:
        """Legacy keyword search retained for deterministic compatibility."""
        q = f"%{query.lower()}%"
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT raw_json FROM cognitive_structures
                WHERE (LOWER(concept) LIKE ? OR LOWER(question) LIKE ?)
                  AND confidence >= ? AND reusable = 1
                ORDER BY confidence DESC, timestamp DESC LIMIT ?
                """,
                (q, q, min_confidence, limit),
            ).fetchall()
        return [CognitiveStructure.from_dict(json.loads(r["raw_json"])) for r in rows]

    def semantic_search(
        self,
        query: str,
        limit: int = 5,
        min_confidence: float = 0.0,
    ) -> list[tuple[CognitiveStructure, float]]:
        """Return ranked semantic candidates as ``(structure, score)``.

        The matcher is a lightweight local approximation, not a learned
        embedding model. Ranking is performed after SQLite filtering so the
        existing persistence model remains unchanged.
        """
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT raw_json FROM cognitive_structures
                WHERE confidence >= ? AND reusable = 1
                ORDER BY confidence DESC, timestamp DESC
                """,
                (min_confidence,),
            ).fetchall()

        structures = [CognitiveStructure.from_dict(json.loads(r["raw_json"])) for r in rows]
        candidates = [
            (s.id, f"{s.concept}. {s.question}. {' '.join(s.tags)}")
            for s in structures
        ]
        ranked = self.semantic_matcher.rank(query, candidates)
        by_id = {s.id: s for s in structures}
        return [
            (by_id[identifier], score)
            for identifier, score in ranked[:limit]
            if self.semantic_matcher.is_relevant(score)
        ]

    def list_all(self, limit: int = 50) -> list[CognitiveStructure]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT raw_json FROM cognitive_structures ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [CognitiveStructure.from_dict(json.loads(r["raw_json"])) for r in rows]

    def count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM cognitive_structures").fetchone()
        return int(row["c"]) if row else 0

    def clear(self) -> None:
        """Dangerous: wipe all memory. Used only by tests / demo reset."""
        with self._connect() as conn:
            conn.execute("DELETE FROM cognitive_structures")
            conn.commit()
