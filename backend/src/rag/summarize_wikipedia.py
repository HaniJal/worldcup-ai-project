"""
One-time ingestion script: fetch the Wikipedia article for the 2026 World
Cup Final, extract the narrative sections we actually want (the match
account, both teams' routes to the final, awards/records), clean up
Wikipedia markup, and chunk it into paragraph-sized pieces ready for
embedding.

This does NOT touch the live web at query time - it's run once, offline,
by a developer, and its output gets embedded and upserted into the same
Qdrant collection as the DB-derived chunks (src/rag/index.py). At query
time, RAG only ever searches the pre-built Qdrant collection.

Run with:
    uv run python -m src.rag.ingest_wikipedia_final
"""

import re

Chunk = tuple[str, dict]


def clean_wikipedia_text(text: str) -> str:
    """Strip Wikipedia-specific markup noise: citation brackets, markdown
    links (keep the link text, drop the URL), stray formatting artifacts."""
    # [[123]](url) or [123](url) style citation markers -> remove entirely
    text = re.sub(r"\[\[?[A-Za-z0-9]{1,4}\]?\]\(\.?/[^)]*\)", "", text)
    text = re.sub(r"\[[A-Za-z0-9]{1,4}\]\(https?://[^)]*\)", "", text)
    # Markdown links [visible text](url) -> just the visible text
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    # Collapse repeated whitespace/newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()


def split_into_paragraphs(text: str, min_length: int = 80) -> list[str]:
    """Split cleaned text into paragraph-sized chunks, dropping anything
    too short to be a useful standalone chunk (stray headers, table
    fragments, etc.)."""
    raw_paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    return [p for p in raw_paragraphs if len(p) >= min_length]


def build_final_match_chunks(raw_match_narrative: str) -> list[Chunk]:
    """
    raw_match_narrative: the cleaned text of the paragraphs describing the
    actual Final match (score, key moments, aftermath, awards).
    """
    paragraphs = split_into_paragraphs(clean_wikipedia_text(raw_match_narrative))
    chunks: list[Chunk] = []
    for para in paragraphs:
        chunks.append(
            (
                para,
                {
                    "type": "external_wiki",
                    "source": "wikipedia_2026_world_cup_final",
                    "topic": "final_match",
                },
            )
        )
    return chunks


def build_route_to_final_chunks(raw_route_text: str, team_name: str) -> list[Chunk]:
    """
    raw_route_text: the cleaned text describing one team's run through the
    knockout stage to reach the final.
    """
    paragraphs = split_into_paragraphs(clean_wikipedia_text(raw_route_text))
    chunks: list[Chunk] = []
    for para in paragraphs:
        chunks.append(
            (
                para,
                {
                    "type": "external_wiki",
                    "source": "wikipedia_2026_world_cup_final",
                    "topic": "route_to_final",
                    "team": team_name,
                },
            )
        )
    return chunks
