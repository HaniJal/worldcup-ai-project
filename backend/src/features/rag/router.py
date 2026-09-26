import asyncio

from fastapi import APIRouter, HTTPException, Request

from src.data.database import DbContext
from src.features.rag.models import AskRequest, AskResponse, SourceChunk
from src.rag.service import answer_question
from src.usage import guardrails
from src.usage.client_ip import get_client_ip

router = APIRouter(prefix="/rag", tags=["rag"])

ENDPOINT_NAME = "rag_ask"


@router.post("/ask", response_model=AskResponse, name="ask_question")
async def ask_question(payload: AskRequest, request: Request, db: DbContext):
    cached = await guardrails.get_cached_response(db, ENDPOINT_NAME, payload.question)
    if cached is not None:
        return AskResponse(**cached)

    ip = get_client_ip(request)

    try:
        await guardrails.check_and_increment_ip_limit(db, ip, ENDPOINT_NAME)
        await guardrails.check_budget(db)
    except guardrails.RateLimitExceeded as exc:
        await db.rollback()
        raise HTTPException(status_code=429, detail=str(exc))
    except guardrails.BudgetExceeded as exc:
        await db.rollback()
        raise HTTPException(status_code=503, detail=str(exc))

    try:
        # answer_question does blocking work (local embedding inference + a
        # network call to Claude), so run it off the event loop.
        result = await asyncio.to_thread(
            answer_question, payload.question, top_k=payload.top_k, type_filter=payload.type_filter
        )
    except Exception as exc:
        # Covers missing API key (RuntimeError) as well as anything
        # unexpected (network errors, model loading failures, etc.) so a
        # failed request always rolls back cleanly instead of surfacing as
        # a raw 500 with no rollback.
        await db.rollback()
        raise HTTPException(status_code=503, detail=f"Failed to answer: {exc}")

    if result.input_tokens or result.output_tokens:
        await guardrails.record_anthropic_spend(
            db, ENDPOINT_NAME, result.input_tokens, result.output_tokens
        )

    response = AskResponse(
        answer=result.answer,
        sources=[
            SourceChunk(text=c.text, score=c.score, metadata=c.metadata)
            for c in result.sources
        ],
    )
    await guardrails.store_cached_response(db, ENDPOINT_NAME, payload.question, response.model_dump())
    await db.commit()

    return response
