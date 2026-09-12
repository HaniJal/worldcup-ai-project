"""
Build the RAG vector index from the seeded database.

Run with:
    uv run python -m src.rag.index

Reads every match/player/team row from Postgres, turns each into a short
text summary (src/rag/summarize.py), embeds all of them locally with
sentence-transformers, and upserts the (text, vector, metadata) triples into
Qdrant. Safe to re-run - point IDs are derived from the text itself, so
re-indexing updates existing entries rather than duplicating them.
"""

import asyncio

from src.data.database import async_session_maker
from src.rag.embeddings import embed_texts, get_embedding_dimension
from src.rag.summarize import build_all_chunks
from src.rag.vector_store import collection_stats, ensure_collection, upsert_chunks

BATCH_SIZE = 64


async def run() -> None:
    print("Loading data from Postgres and building text chunks...")
    async with async_session_maker() as db:
        chunks = await build_all_chunks(db)
    print(f"  {len(chunks)} chunks ready (teams, players, matches).")

    print("Loading embedding model (first run downloads the model, ~90MB)...")
    dim = get_embedding_dimension()
    print(f"  Embedding dimension: {dim}")

    ensure_collection(vector_size=dim)

    print(f"Embedding and upserting in batches of {BATCH_SIZE}...")
    total = 0
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        texts = [text for text, _ in batch]
        vectors = embed_texts(texts)
        count = upsert_chunks(batch, vectors)
        total += count
        print(f"  {total}/{len(chunks)}")

    stats = collection_stats()
    print(f"Done. Collection now has {stats['points_count']} points.")


if __name__ == "__main__":
    asyncio.run(run())
