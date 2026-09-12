import asyncio

from fastapi import APIRouter, HTTPException

from src.features.rag.models import AskRequest, AskResponse, SourceChunk
from src.rag.service import answer_question

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/ask", response_model=AskResponse, name="ask_question")
async def ask_question(payload: AskRequest):
    try:
        # answer_question does blocking work (local embedding inference + a
        # network call to Claude), so run it off the event loop.
        result = await asyncio.to_thread(
            answer_question, payload.question, top_k=payload.top_k, type_filter=payload.type_filter
        )
    except RuntimeError as exc:
        # e.g. missing ANTHROPIC_API_KEY
        raise HTTPException(status_code=503, detail=str(exc))

    return AskResponse(
        answer=result.answer,
        sources=[
            SourceChunk(text=c.text, score=c.score, metadata=c.metadata)
            for c in result.sources
        ],
    )
