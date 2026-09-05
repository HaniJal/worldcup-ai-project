from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from src.data.database import DbContext
from src.features.matches import service
from src.features.matches.models import MatchDetail, MatchSummary

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[MatchSummary], name="list_matches")
async def list_matches(
    db: DbContext,
    stage_id: UUID | None = Query(default=None),
    team_id: UUID | None = Query(default=None),
):
    return await service.list_matches(db, stage_id=stage_id, team_id=team_id)


@router.get("/{match_id}", response_model=MatchDetail, name="get_match")
async def get_match(match_id: UUID, db: DbContext):
    match = await service.get_match(db, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match
