from fastapi import APIRouter, HTTPException

from src.data.database import DbContext
from src.features.agent.models import AgentAskRequest, AgentAskResponse, ToolCallOut
from src.agent.orchestrator import run_agent

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/ask", response_model=AgentAskResponse, name="agent_ask")
async def agent_ask(payload: AgentAskRequest, db: DbContext):
    try:
        result = await run_agent(payload.question, db)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return AgentAskResponse(
        answer=result.answer,
        tool_calls=[
            ToolCallOut(name=c.name, input=c.input, result=c.result) for c in result.tool_calls
        ],
    )
