"""
One-time enrichment of the RAG knowledge base: adds a small number of
hand-picked, fact-checked paragraphs from Wikipedia's "2026 FIFA World Cup
final" article into the same Qdrant collection used by the DB-derived
chunks (src/rag/index.py).

Why this exists: the DB-derived match summaries describe results
mechanically ("Team A beat Team B X-Y") but never narrate the story of the
Final specifically in the way people actually ask about it ("who was best
in the final", "how did Spain get to the final"). This adds that missing
narrative content - once, offline - so RAG retrieval has a chance of
finding it.

The source text in wikipedia_final_content.py was fetched from Wikipedia
and every key fact (winner, score, Man of the Match, date, runner-up) was
cross-checked against the seeded database before inclusion. Do not add
other web content this way without doing the same cross-check - a source
that disagrees with the verified database would make RAG contradict
itself.

Run with:
    uv run python -m src.rag.ingest_wikipedia_final
"""

from src.rag.embeddings import embed_texts, get_embedding_dimension
from src.rag.summarize_wikipedia import build_final_match_chunks, build_route_to_final_chunks
from src.rag.vector_store import ensure_collection, upsert_chunks
from src.rag.wikipedia_final_content import (
    ARGENTINA_ROUTE_NARRATIVE,
    FINAL_MATCH_NARRATIVE,
    SPAIN_ROUTE_NARRATIVE,
)


def build_all_wikipedia_chunks():
    chunks = []
    chunks += build_final_match_chunks(FINAL_MATCH_NARRATIVE)
    chunks += build_route_to_final_chunks(SPAIN_ROUTE_NARRATIVE, "Spain")
    chunks += build_route_to_final_chunks(ARGENTINA_ROUTE_NARRATIVE, "Argentina")
    return chunks


def run() -> None:
    print("Building chunks from the Wikipedia Final article (fact-checked against the DB)...")
    chunks = build_all_wikipedia_chunks()
    print(f"  {len(chunks)} chunks ready.")

    print("Loading embedding model...")
    dim = get_embedding_dimension()
    ensure_collection(vector_size=dim)

    print("Embedding and upserting...")
    texts = [text for text, _ in chunks]
    vectors = embed_texts(texts)
    count = upsert_chunks(chunks, vectors)
    print(f"Done. Upserted {count} Wikipedia-derived chunks.")


if __name__ == "__main__":
    run()
