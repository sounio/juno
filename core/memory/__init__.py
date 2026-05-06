"""Memory System: Short-term, Long-term, Vector Store."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime, timezone
import json


class Memory(ABC):
    @abstractmethod
    async def save(self, key: str, data: Any, namespace: str = "default"):
        pass

    @abstractmethod
    async def load(self, key: str, namespace: str = "default") -> Optional[Any]:
        pass

    @abstractmethod
    async def search(self, query: str, namespace: str = "default", top_k: int = 5) -> list[Any]:
        pass


class ShortTermMemory(Memory):
    """In-memory cache with TTL."""

    def __init__(self, ttl: int = 3600):
        self._store: dict[str, tuple[Any, float]] = {}
        self._ttl = ttl

    async def save(self, key: str, data: Any, namespace: str = "default"):
        full_key = f"{namespace}:{key}"
        self._store[full_key] = (data, datetime.now(timezone.utc).timestamp())

    async def load(self, key: str, namespace: str = "default") -> Optional[Any]:
        full_key = f"{namespace}:{key}"
        entry = self._store.get(full_key)
        if not entry:
            return None
        data, ts = entry
        if datetime.now(timezone.utc).timestamp() - ts > self._ttl:
            del self._store[full_key]
            return None
        return data

    async def search(self, query: str, namespace: str = "default", top_k: int = 5) -> list[Any]:
        prefix = f"{namespace}:"
        results = []
        for key, (data, ts) in self._store.items():
            if key.startswith(prefix) and query.lower() in str(data).lower():
                results.append({"key": key, "data": data, "score": 1.0})
        return results[:top_k]


class LongTermMemory(Memory):
    """SQLite-backed persistent memory."""

    def __init__(self, db_path: str = "./data/memory.db"):
        import sqlite3
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                namespace TEXT, key TEXT, value TEXT,
                created_at TEXT, updated_at TEXT,
                PRIMARY KEY (namespace, key)
            )
        """)
        self._conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts
            USING fts5(namespace, key, value)
        """)
        self._conn.commit()

    async def save(self, key: str, data: Any, namespace: str = "default"):
        now = datetime.now(timezone.utc).isoformat()
        value = json.dumps(data) if not isinstance(data, str) else data
        self._conn.execute(
            "INSERT OR REPLACE INTO memory (namespace, key, value, created_at, updated_at) VALUES (?,?,?,COALESCE((SELECT created_at FROM memory WHERE namespace=? AND key=?),?),?)",
            (namespace, key, value, namespace, key, now, now),
        )
        self._conn.execute(
            "INSERT OR REPLACE INTO memory_fts (namespace, key, value) VALUES (?,?,?)",
            (namespace, key, value),
        )
        self._conn.commit()

    async def load(self, key: str, namespace: str = "default") -> Optional[Any]:
        cursor = self._conn.execute(
            "SELECT value FROM memory WHERE namespace=? AND key=?",
            (namespace, key),
        )
        row = cursor.fetchone()
        if not row:
            return None
        try:
            return json.loads(row[0])
        except (json.JSONDecodeError, TypeError):
            return row[0]

    async def search(self, query: str, namespace: str = "default", top_k: int = 5) -> list[Any]:
        cursor = self._conn.execute(
            "SELECT key, value, rank FROM memory_fts WHERE namespace=? AND value MATCH ? ORDER BY rank LIMIT ?",
            (namespace, query, top_k),
        )
        return [
            {"key": row[0], "data": row[1], "score": 1.0 / (row[2] + 1)}
            for row in cursor.fetchall()
        ]


class VectorMemory(Memory):
    """ChromaDB vector store for embeddings-based retrieval."""

    def __init__(self, persist_dir: str = "./data/chroma"):
        import chromadb
        self._client = chromadb.PersistentClient(path=persist_dir)

    async def save(self, key: str, data: Any, namespace: str = "default"):
        collection = self._client.get_or_create_collection(name=namespace)
        collection.add(
            ids=[key],
            documents=[json.dumps(data) if not isinstance(data, str) else data],
        )

    async def load(self, key: str, namespace: str = "default") -> Optional[Any]:
        collection = self._client.get_or_create_collection(name=namespace)
        results = collection.get(ids=[key])
        if not results["documents"]:
            return None
        doc = results["documents"][0]
        try:
            return json.loads(doc)
        except (json.JSONDecodeError, TypeError):
            return doc

    async def search(self, query: str, namespace: str = "default", top_k: int = 5) -> list[Any]:
        collection = self._client.get_or_create_collection(name=namespace)
        results = collection.query(query_texts=[query], n_results=top_k)
        return [
            {"key": id, "data": doc, "score": dist}
            for id, doc, dist in zip(
                results["ids"][0],
                results["documents"][0],
                results["distances"][0],
            )
        ]
