from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlayerSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    player_name: str
    position: str | None
    club_team: str | None
    market_value_eur: float | None
    caps: int | None
    date_of_birth: date | None
    height_cm: int | None


class TeamSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    team_name: str
    fifa_code: str
    group_letter: str
    confederation: str
    fifa_ranking: int | None
    elo_rating: float | None
    manager_name: str | None


class TeamDetail(TeamSummary):
    players: list[PlayerSummary] = []
