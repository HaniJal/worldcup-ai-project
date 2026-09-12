from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    type_filter: str | None = Field(
        default=None, description="Restrict retrieval to 'team', 'player', or 'match' chunks"
    )


class SourceChunk(BaseModel):
    text: str
    score: float
    metadata: dict


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
