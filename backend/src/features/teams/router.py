from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from src.data.database import DbContext
from src.features.teams import service
from src.features.teams.models import TeamDetail, TeamSummary

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamSummary], name="list_teams")
async def list_teams(
    db: DbContext,
    group_letter: str | None = Query(default=None, description="Filter by group, e.g. 'A'"),
):
    teams = await service.list_teams(db, group_letter=group_letter)
    return teams


@router.get("/{team_id}", response_model=TeamDetail, name="get_team")
async def get_team(team_id: UUID, db: DbContext):
    team = await service.get_team(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
