import re
import enum
from datetime import datetime, date
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, Date, Integer, Float, Boolean, Enum, ForeignKey
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column, relationship, declared_attr

def camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)    
    
# Enums
class MatchStatus(enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"

class MatchStage(enum.Enum):
    GROUP = "group"
    ROUND_OF_32 = "round_of_32"      
    ROUND_OF_16 = "round_of_16"
    QUARTER_FINAL = "quarter_final"
    SEMI_FINAL = "semi_final"
    THIRD_PLACE = "third_place"
    FINAL = "final"

class PlayerPosition(enum.Enum):
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"

class EventType(enum.Enum):
    GOAL = "goal"
    ASSIST = "assist"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    SUBSTITUTION = "substitution"
    VAR = "var"

class Group(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    J = "J"
    K = "K"
    L = "L"

class Team(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[int] = mapped_column(Integer, unique=True)  # dataset's team_id
    team_name: Mapped[str] = mapped_column(String(100), nullable=False)
    fifa_code: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)
    group_letter: Mapped[str] = mapped_column(String(1), nullable=False)
    confederation: Mapped[str] = mapped_column(String(20), nullable=False)
    fifa_ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    elo_rating: Mapped[float] = mapped_column(Float, nullable=True)
    manager_name: Mapped[str] = mapped_column(String(100), nullable=True)

    players: Mapped[list["Player"]] = relationship(back_populates="team")


class Venue(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[int] = mapped_column(Integer, unique=True)  # dataset's venue_id
    stadium_name: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=True)
    latitude: Mapped[str] = mapped_column(String(20), nullable=True)
    longitude: Mapped[str] = mapped_column(String(20), nullable=True)
    elevation_meters: Mapped[int] = mapped_column(Integer, nullable=True)

    matches: Mapped[list["Match"]] = relationship(back_populates="venue")


class TournamentStage(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[int] = mapped_column(Integer, unique=True)  # dataset's stage_id
    stage_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_knockout: Mapped[bool] = mapped_column(Boolean, default=False)

    matches: Mapped[list["Match"]] = relationship(back_populates="stage")


class Referee(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[int] = mapped_column(Integer, unique=True)  # dataset's referee_id
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    avg_cards_per_game: Mapped[float] = mapped_column(Float, nullable=True)

    matches: Mapped[list["Match"]] = relationship(back_populates="referee")


class Player(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[int] = mapped_column(Integer, unique=True)  # dataset's player_id
    team_id: Mapped[UUID] = mapped_column(ForeignKey("team.id"), nullable=False)
    player_name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(10), nullable=True)
    club_team: Mapped[str] = mapped_column(String(100), nullable=True)
    market_value_eur: Mapped[float] = mapped_column(Float, nullable=True)
    caps: Mapped[int] = mapped_column(Integer, nullable=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    height_cm: Mapped[int] = mapped_column(Integer, nullable=True)

    team: Mapped["Team"] = relationship(back_populates="players")
    stats: Mapped["PlayerStats"] = relationship(
        back_populates="player", uselist=False
    )


class Match(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[int] = mapped_column(Integer, unique=True)  # dataset's match_id
    stage_id: Mapped[UUID] = mapped_column(
        ForeignKey("tournament_stage.id"), nullable=True
    )
    venue_id: Mapped[UUID] = mapped_column(ForeignKey("venue.id"), nullable=True)
    home_team_id: Mapped[UUID] = mapped_column(ForeignKey("team.id"), nullable=False)
    away_team_id: Mapped[UUID] = mapped_column(ForeignKey("team.id"), nullable=False)
    referee_id: Mapped[UUID] = mapped_column(ForeignKey("referee.id"), nullable=True)
    player_of_the_match_id: Mapped[UUID] = mapped_column(
        ForeignKey("player.id"), nullable=True
    )
    match_date: Mapped[date] = mapped_column(Date, nullable=True)
    kickoff_time: Mapped[str] = mapped_column(String(10), nullable=True)
    home_score: Mapped[int] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int] = mapped_column(Integer, nullable=True)
    home_penalties: Mapped[int] = mapped_column(Integer, nullable=True)
    away_penalties: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=True)
    result_type: Mapped[str] = mapped_column(String(20), nullable=True)
    home_xg: Mapped[float] = mapped_column(Float, nullable=True)
    away_xg: Mapped[float] = mapped_column(Float, nullable=True)

    stage: Mapped["TournamentStage"] = relationship(back_populates="matches")
    venue: Mapped["Venue"] = relationship(back_populates="matches")
    referee: Mapped["Referee"] = relationship(back_populates="matches")
    home_team: Mapped["Team"] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped["Team"] = relationship(foreign_keys=[away_team_id])
    player_of_the_match: Mapped["Player"] = relationship(
        foreign_keys=[player_of_the_match_id]
    )
    events: Mapped[list["MatchEvent"]] = relationship(back_populates="match")
    team_stats: Mapped[list["MatchTeamStats"]] = relationship(back_populates="match")
    lineups: Mapped[list["MatchLineup"]] = relationship(back_populates="match")


class MatchEvent(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[int] = mapped_column(Integer, unique=True)
    match_id: Mapped[UUID] = mapped_column(ForeignKey("match.id"), nullable=False)
    team_id: Mapped[UUID] = mapped_column(ForeignKey("team.id"), nullable=False)
    player_id: Mapped[UUID] = mapped_column(ForeignKey("player.id"), nullable=True)
    minute: Mapped[int] = mapped_column(Integer, nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)

    match: Mapped["Match"] = relationship(back_populates="events")


class MatchTeamStats(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    match_id: Mapped[UUID] = mapped_column(ForeignKey("match.id"), nullable=False)
    team_id: Mapped[UUID] = mapped_column(ForeignKey("team.id"), nullable=False)
    possession_pct: Mapped[int] = mapped_column(Integer, nullable=True)
    total_shots: Mapped[int] = mapped_column(Integer, nullable=True)
    shots_on_target: Mapped[int] = mapped_column(Integer, nullable=True)
    corners: Mapped[int] = mapped_column(Integer, nullable=True)
    fouls: Mapped[int] = mapped_column(Integer, nullable=True)
    offsides: Mapped[int] = mapped_column(Integer, nullable=True)
    saves: Mapped[int] = mapped_column(Integer, nullable=True)
    player_of_the_match: Mapped[str] = mapped_column(String(100), nullable=True)

    match: Mapped["Match"] = relationship(back_populates="team_stats")


class MatchLineup(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[int] = mapped_column(Integer, unique=True)
    match_id: Mapped[UUID] = mapped_column(ForeignKey("match.id"), nullable=False)
    team_id: Mapped[UUID] = mapped_column(ForeignKey("team.id"), nullable=False)
    player_id: Mapped[UUID] = mapped_column(ForeignKey("player.id"), nullable=False)
    is_starting: Mapped[bool] = mapped_column(Boolean, default=False)
    tactical_position: Mapped[str] = mapped_column(String(10), nullable=True)
    minutes_played: Mapped[int] = mapped_column(Integer, nullable=True)

    match: Mapped["Match"] = relationship(back_populates="lineups")


class PlayerStats(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    player_id: Mapped[UUID] = mapped_column(
        ForeignKey("player.id"), nullable=False, unique=True
    )
    team_id: Mapped[UUID] = mapped_column(ForeignKey("team.id"), nullable=False)
    position: Mapped[str] = mapped_column(String(10), nullable=True)
    matches_played: Mapped[int] = mapped_column(Integer, default=0)
    matches_started: Mapped[int] = mapped_column(Integer, default=0)
    minutes_played: Mapped[int] = mapped_column(Integer, default=0)
    goals: Mapped[int] = mapped_column(Integer, default=0)
    assists: Mapped[int] = mapped_column(Integer, default=0)
    shots: Mapped[int] = mapped_column(Integer, nullable=True)
    shots_on_target: Mapped[int] = mapped_column(Integer, nullable=True)
    yellow_cards: Mapped[int] = mapped_column(Integer, default=0)
    red_cards: Mapped[int] = mapped_column(Integer, default=0)
    penalty_goals: Mapped[int] = mapped_column(Integer, default=0)
    own_goals: Mapped[int] = mapped_column(Integer, default=0)
    clean_sheets: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    goals_conceded: Mapped[int] = mapped_column(Integer, default=0)
    average_rating: Mapped[float] = mapped_column(Float, nullable=True)
    data_source: Mapped[str] = mapped_column(String(50), nullable=True)

    player: Mapped["Player"] = relationship(back_populates="stats")