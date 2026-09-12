"""
The actual RAG loop: take a natural-language question, retrieve the most
relevant chunks from Qdrant, and ask Claude to answer using only that
context.
"""

from dataclasses import dataclass

from anthropic import Anthropic

from src.rag.embeddings import embed_query
from src.rag.vector_store import RetrievedChunk, search
from src.settings import settings

SYSTEM_PROMPT = """You are a knowledgeable assistant for the FIFA World Cup 2026. \
Answer the user's question using ONLY the information in the provided context. \
If the context doesn't contain enough information to answer confidently, say so \
plainly rather than guessing or using outside knowledge. Keep answers concise \
and factual. When useful, mention specific numbers (scores, goals, dates) from \
the context."""


@dataclass
class RAGAnswer:
    answer: str
    sources: list[RetrievedChunk]


def _build_context(chunks: list[RetrievedChunk]) -> str:
    return "\n\n".join(f"- {chunk.text}" for chunk in chunks)


def retrieve(question: str, top_k: int = 5, type_filter: str | None = None) -> list[RetrievedChunk]:
    query_vector = embed_query(question)
    return search(query_vector, top_k=top_k, type_filter=type_filter)


def generate_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    if not settings.ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to your .env to enable answer generation."
        )

    if not chunks:
        return "I couldn't find any relevant information in the World Cup data to answer that."

    context = _build_context(chunks)
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    message = client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            }
        ],
    )
    return "".join(block.text for block in message.content if block.type == "text")


def answer_question(question: str, top_k: int = 5, type_filter: str | None = None) -> RAGAnswer:
    chunks = retrieve(question, top_k=top_k, type_filter=type_filter)
    answer = generate_answer(question, chunks)
    return RAGAnswer(answer=answer, sources=chunks)
