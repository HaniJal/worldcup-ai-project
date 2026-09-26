from fastapi import APIRouter, HTTPException, Request

from src.data.database import DbContext
from src.features.agent.models import AgentAskRequest, AgentAskResponse, ToolCallOut
from src.agent.orchestrator import run_agent
from src.usage import guardrails
from src.usage.client_ip import get_client_ip

router = APIRouter(prefix="/agent", tags=["agent"])

ENDPOINT_NAME = "agent_ask"


@router.post("/ask", response_model=AgentAskResponse, name="agent_ask")
async def agent_ask(payload: AgentAskRequest, request: Request, db: DbContext):
    cached = await guardrails.get_cached_response(db, ENDPOINT_NAME, payload.question)
    if cached is not None:
        return AgentAskResponse(**cached)

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
        result = await run_agent(payload.question, db)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=503, detail=str(exc))

    response = AgentAskResponse(
        answer=result.answer,
        tool_calls=[
            ToolCallOut(name=c.name, input=c.input, result=c.result) for c in result.tool_calls
        ],
    )
    await guardrails.store_cached_response(db, ENDPOINT_NAME, payload.question, response.model_dump())
    await db.commit()

    return response
