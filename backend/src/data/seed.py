"""
Seed the database from the World Cup 2026 dataset CSVs.

Run with:
    uv run python -m src.data.seed          # seed (skips if data already present)
    uv run python -m src.data.seed --reset  # wipe all tables first, then reseed

The CSVs live in src/data/seed_data/. Insert order matters because of foreign
keys: independent lookup tables first (Team, Venue, TournamentStage, Referee),
then Player (needs Team), then Match (needs the lookups + Player for
player_of_the_match), then everything that hangs off a Match/Player
(MatchEvent, MatchTeamStats, MatchLineup, PlayerStats).

We keep an in-memory {csv_id: generated_uuid} map per entity so later tables
can resolve their foreign keys without a round trip to the DB.
"""

import argparse
import asyncio
import math
from datetime import date, datetime
from pathlib import Path
from uuid import UUID

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database import Base, async_session_maker, engine
from src.data.sql_models import (
    Match,
    MatchEvent,
    MatchLineup,
    MatchTeamStats,
    Player,
    PlayerStats,
    Referee,
    Team,
    TournamentStage,
    Venue,
)

SEED_DIR = Path(__file__).resolve().parent / "seed_data"


def clean(value):
    """Turn pandas NaN/NaT into None; leave everything else untouched."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if pd.isna(value):
        return None
    return value


def clean_int(value) -> int | None:
    value = clean(value)
    return int(value) if value is not None else None


def clean_float(value) -> float | None:
    value = clean(value)
    return float(value) if value is not None else None


def clean_bool(value) -> bool:
    value = clean(value)
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)


def clean_date(value) -> date | None:
    value = clean(value)
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


async def reset_tables(session: AsyncSession) -> None:
    """Truncate every mapped table, restarting identity and cascading FKs."""
    table_names = ", ".join(t.name for t in Base.metadata.sorted_tables)
    await session.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))
    await session.commit()


async def already_seeded(session: AsyncSession) -> bool:
    result = await session.execute(text("SELECT COUNT(*) FROM team"))
    return result.scalar_one() > 0


async def seed_teams(session: AsyncSession) -> dict[int, UUID]:
    df = pd.read_csv(SEED_DIR / "teams.csv")
    id_map = {}
    for row in df.itertuples(index=False):
        team = Team(
            source_id=row.team_id,
            team_name=row.team_name,
            fifa_code=row.fifa_code,
            group_letter=row.group_letter,
            confederation=row.confederation,
            fifa_ranking=clean_int(row.fifa_ranking_pre_tournament),
            elo_rating=clean_float(row.elo_rating),
            manager_name=clean(row.manager_name),
        )
        session.add(team)
        id_map[row.team_id] = team
    await session.flush()
    return {source_id: team.id for source_id, team in id_map.items()}


async def seed_venues(session: AsyncSession) -> dict[int, UUID]:
    df = pd.read_csv(SEED_DIR / "venues.csv")
    id_map = {}
    for row in df.itertuples(index=False):
        venue = Venue(
            source_id=row.venue_id,
            stadium_name=row.stadium_name,
            city=row.city,
            country=row.country,
            capacity=clean_int(row.capacity),
            latitude=str(clean(row.latitude)) if clean(row.latitude) is not None else None,
            longitude=str(clean(row.longitude)) if clean(row.longitude) is not None else None,
            elevation_meters=clean_int(row.elevation_meters),
        )
        session.add(venue)
        id_map[row.venue_id] = venue
    await session.flush()
    return {source_id: v.id for source_id, v in id_map.items()}


async def seed_stages(session: AsyncSession) -> dict[int, UUID]:
    df = pd.read_csv(SEED_DIR / "tournament_stages.csv")
    id_map = {}
    for row in df.itertuples(index=False):
        stage = TournamentStage(
            source_id=row.stage_id,
            stage_name=row.stage_name,
            is_knockout=clean_bool(row.is_knockout),
        )
        session.add(stage)
        id_map[row.stage_id] = stage
    await session.flush()
    return {source_id: s.id for source_id, s in id_map.items()}


async def seed_referees(session: AsyncSession) -> dict[int, UUID]:
    df = pd.read_csv(SEED_DIR / "referees.csv")
    id_map = {}
    for row in df.itertuples(index=False):
        ref = Referee(
            source_id=row.referee_id,
            name=row.name,
            country=clean(row.country),
            avg_cards_per_game=clean_float(row.avg_cards_per_game),
        )
        session.add(ref)
        id_map[row.referee_id] = ref
    await session.flush()
    return {source_id: r.id for source_id, r in id_map.items()}


async def seed_players(session: AsyncSession, team_ids: dict[int, UUID]) -> dict[int, UUID]:
    df = pd.read_csv(SEED_DIR / "squads_and_players.csv")
    id_map = {}
    for row in df.itertuples(index=False):
        player = Player(
            source_id=row.player_id,
            team_id=team_ids[row.team_id],
            player_name=row.player_name,
            position=clean(row.position),
            club_team=clean(row.club_team),
            market_value_eur=clean_float(row.market_value_eur),
            caps=clean_int(row.caps),
            date_of_birth=clean_date(row.date_of_birth),
            height_cm=clean_int(row.height_cm),
        )
        session.add(player)
        id_map[row.player_id] = player
    await session.flush()
    return {source_id: p.id for source_id, p in id_map.items()}


async def seed_matches(
    session: AsyncSession,
    stage_ids: dict[int, UUID],
    venue_ids: dict[int, UUID],
    team_ids: dict[int, UUID],
    referee_ids: dict[int, UUID],
    player_ids: dict[int, UUID],
) -> dict[int, UUID]:
    df = pd.read_csv(SEED_DIR / "matches.csv")
    id_map = {}
    for row in df.itertuples(index=False):
        potm = clean_int(row.player_of_the_match_id)
        match = Match(
            source_id=row.match_id,
            stage_id=stage_ids.get(row.stage_id),
            venue_id=venue_ids.get(row.venue_id),
            home_team_id=team_ids[row.home_team_id],
            away_team_id=team_ids[row.away_team_id],
            referee_id=referee_ids.get(row.referee_id),
            player_of_the_match_id=player_ids.get(potm) if potm is not None else None,
            match_date=clean_date(row.date),
            kickoff_time=clean(row.kickoff_time_utc),
            home_score=clean_int(row.home_score),
            away_score=clean_int(row.away_score),
            home_penalties=clean_int(row.home_penalty_score),
            away_penalties=clean_int(row.away_penalty_score),
            status=clean(row.status),
            result_type=clean(row.result_type),
            home_xg=clean_float(row.home_xg),
            away_xg=clean_float(row.away_xg),
        )
        session.add(match)
        id_map[row.match_id] = match
    await session.flush()
    return {source_id: m.id for source_id, m in id_map.items()}


async def seed_match_events(
    session: AsyncSession,
    match_ids: dict[int, UUID],
    team_ids: dict[int, UUID],
    player_ids: dict[int, UUID],
) -> None:
    df = pd.read_csv(SEED_DIR / "match_events.csv")
    for row in df.itertuples(index=False):
        pid = clean_int(row.player_id)
        session.add(
            MatchEvent(
                source_id=row.event_id,
                match_id=match_ids[row.match_id],
                team_id=team_ids[row.team_id],
                player_id=player_ids.get(pid) if pid is not None else None,
                minute=clean_int(row.minute),
                event_type=row.event_type,
            )
        )
    await session.flush()


async def seed_match_team_stats(
    session: AsyncSession, match_ids: dict[int, UUID], team_ids: dict[int, UUID]
) -> None:
    df = pd.read_csv(SEED_DIR / "match_team_stats.csv")
    for row in df.itertuples(index=False):
        session.add(
            MatchTeamStats(
                match_id=match_ids[row.match_id],
                team_id=team_ids[row.team_id],
                possession_pct=clean_int(row.possession_pct),
                total_shots=clean_int(row.total_shots),
                shots_on_target=clean_int(row.shots_on_target),
                corners=clean_int(row.corners),
                fouls=clean_int(row.fouls),
                offsides=clean_int(row.offsides),
                saves=clean_int(row.saves),
                player_of_the_match=clean(row.player_of_the_match),
            )
        )
    await session.flush()


async def seed_match_lineups(
    session: AsyncSession,
    match_ids: dict[int, UUID],
    team_ids: dict[int, UUID],
    player_ids: dict[int, UUID],
) -> None:
    df = pd.read_csv(SEED_DIR / "match_lineups.csv")
    for row in df.itertuples(index=False):
        session.add(
            MatchLineup(
                source_id=row.lineup_id,
                match_id=match_ids[row.match_id],
                team_id=team_ids[row.team_id],
                player_id=player_ids[row.player_id],
                is_starting=clean_bool(row.is_starting_xi),
                tactical_position=clean(row.tactical_position),
                minutes_played=clean_int(row.minutes_played),
            )
        )
    await session.flush()


async def seed_player_stats(
    session: AsyncSession, player_ids: dict[int, UUID], team_ids: dict[int, UUID]
) -> None:
    df = pd.read_csv(SEED_DIR / "player_stats.csv")
    for row in df.itertuples(index=False):
        session.add(
            PlayerStats(
                player_id=player_ids[row.player_id],
                team_id=team_ids[row.team_id],
                position=clean(row.position),
                matches_played=clean_int(row.matches_played) or 0,
                matches_started=clean_int(row.matches_started) or 0,
                minutes_played=clean_int(row.minutes_played) or 0,
                goals=clean_int(row.goals) or 0,
                assists=clean_int(row.assists) or 0,
                shots=clean_int(row.shots),
                shots_on_target=clean_int(row.shots_on_target),
                yellow_cards=clean_int(row.yellow_cards) or 0,
                red_cards=clean_int(row.red_cards) or 0,
                penalty_goals=clean_int(row.penalty_goals) or 0,
                own_goals=clean_int(row.own_goals) or 0,
                clean_sheets=clean_int(row.clean_sheets) or 0,
                saves=clean_int(row.saves) or 0,
                goals_conceded=clean_int(row.goals_conceded) or 0,
                average_rating=clean_float(row.average_rating),
                data_source=clean(row.data_source),
            )
        )
    await session.flush()


async def run(reset: bool) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        if reset:
            print("Resetting tables...")
            await reset_tables(session)
        elif await already_seeded(session):
            print("Database already has data. Run with --reset to wipe and reseed.")
            return

        print("Seeding teams, venues, stages, referees...")
        team_ids = await seed_teams(session)
        venue_ids = await seed_venues(session)
        stage_ids = await seed_stages(session)
        referee_ids = await seed_referees(session)

        print("Seeding players...")
        player_ids = await seed_players(session, team_ids)

        print("Seeding matches...")
        match_ids = await seed_matches(
            session, stage_ids, venue_ids, team_ids, referee_ids, player_ids
        )

        print("Seeding match events, team stats, lineups, player stats...")
        await seed_match_events(session, match_ids, team_ids, player_ids)
        await seed_match_team_stats(session, match_ids, team_ids)
        await seed_match_lineups(session, match_ids, team_ids, player_ids)
        await seed_player_stats(session, player_ids, team_ids)

        await session.commit()
        print(
            f"Done. Seeded {len(team_ids)} teams, {len(player_ids)} players, "
            f"{len(match_ids)} matches."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Wipe all tables before seeding")
    args = parser.parse_args()
    asyncio.run(run(reset=args.reset))