from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TeamRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    team_name: str
    fifa_code: str


class VenueRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    stadium_name: str
    city: str
    country: str


class StageRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    stage_name: str
    is_knockout: bool


class RefereeRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class MatchEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    minute: int | None
    event_type: str
    team_id: UUID
    player_id: UUID | None


class MatchTeamStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: UUID
    possession_pct: int | None
    total_shots: int | None
    shots_on_target: int | None
    corners: int | None
    fouls: int | None
    offsides: int | None
    saves: int | None
    player_of_the_match: str | None


class MatchSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    match_date: date | None
    kickoff_time: str | None
    status: str | None
    home_team: TeamRef
    away_team: TeamRef
    home_score: int | None
    away_score: int | None
    stage: StageRef | None
    venue: VenueRef | None


class MatchDetail(MatchSummary):
    referee: RefereeRef | None
    home_xg: float | None
    away_xg: float | None
    result_type: str | None
    events: list[MatchEventOut] = []
    team_stats: list[MatchTeamStatsOut] = []
