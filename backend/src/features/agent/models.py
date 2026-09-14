from pydantic import BaseModel, Field


class AgentAskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class ToolCallOut(BaseModel):
    name: str
    input: dict
    result: object


class AgentAskResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCallOut]
