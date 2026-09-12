"""
Thin wrapper around the Qdrant client - collection setup, upserting embedded
chunks, and similarity search. Keeps Qdrant-specific details (point IDs,
payload shape, distance metric) out of the rest of the app.
"""

import hashlib
import uuid
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from src.settings import settings


@dataclass
class RetrievedChunk:
    text: str
    metadata: dict
    score: float


def get_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL)


def _stable_point_id(text: str) -> str:
    """
    Deterministic UUID derived from the chunk text, so re-running the
    indexing script updates existing points instead of duplicating them.
    """
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return str(uuid.UUID(digest[:32]))


def ensure_collection(vector_size: int) -> None:
    client = get_client()
    if not client.collection_exists(settings.QDRANT_COLLECTION):
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


def upsert_chunks(chunks: list[tuple[str, dict]], vectors: list[list[float]]) -> int:
    """chunks: list of (text, metadata). vectors: matching list of embeddings."""
    client = get_client()
    points = [
        PointStruct(
            id=_stable_point_id(text),
            vector=vector,
            payload={"text": text, **metadata},
        )
        for (text, metadata), vector in zip(chunks, vectors)
    ]
    client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
    return len(points)


def search(query_vector: list[float], top_k: int = 5, type_filter: str | None = None) -> list[RetrievedChunk]:
    client = get_client()

    query_filter = None
    if type_filter:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        query_filter = Filter(
            must=[FieldCondition(key="type", match=MatchValue(value=type_filter))]
        )

    results = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        query_filter=query_filter,
    ).points

    return [
        RetrievedChunk(
            text=point.payload.get("text", ""),
            metadata={k: v for k, v in point.payload.items() if k != "text"},
            score=point.score,
        )
        for point in results
    ]


def collection_stats() -> dict:
    client = get_client()
    if not client.collection_exists(settings.QDRANT_COLLECTION):
        return {"exists": False, "points_count": 0}
    info = client.get_collection(settings.QDRANT_COLLECTION)
    return {"exists": True, "points_count": info.points_count}
