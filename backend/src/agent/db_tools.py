"""
Predefined, parameterized query functions the agent can call.

Deliberately NOT a text-to-SQL tool: the agent picks one of these named
functions and supplies simple arguments (a team name, a player name, a
limit). Every query here is fixed and reviewed ahead of time, so there's no
risk of the model generating an expensive, wrong, or unsafe query - the
"tool" is the function signature, not raw SQL.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data.sql_models import Match, Player, PlayerStats, Team


async def get_top_scorers(db: AsyncSession, limit: int = 5, team_name: str | None = None) -> list[dict]:
    stmt = (
        select(PlayerStats)
        .join(Player, PlayerStats.player_id == Player.id)
        .join(Team, Player.team_id == Team.id)
        .options(selectinload(PlayerStats.player).selectinload(Player.team))
        .order_by(PlayerStats.goals.desc())
        .limit(limit)
    )
    if team_name:
        stmt = stmt.where(Team.team_name.ilike(f"%{team_name}%"))

    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [
        {
            "player_name": row.player.player_name,
            "team": row.player.team.team_name,
            "goals": row.goals,
            "assists": row.assists,
            "matches_played": row.matches_played,
        }
        for row in rows
    ]


async def get_team_record(db: AsyncSession, team_name: str) -> dict:
    stmt = select(Team).where(Team.team_name.ilike(f"%{team_name}%"))
    result = await db.execute(stmt)
    team = result.scalars().first()
    if team is None:
        return {"error": f"No team found matching '{team_name}'"}

    stmt = (
        select(Match)
        .where((Match.home_team_id == team.id) | (Match.away_team_id == team.id))
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
            selectinload(Match.stage),
        )
        .order_by(Match.match_date)
    )
    result = await db.execute(stmt)
    matches = result.scalars().all()

    wins = draws = losses = goals_for = goals_against = 0
    match_list = []
    furthest_stage = None
    for m in matches:
        if m.home_score is None or m.away_score is None:
            continue
        is_home = m.home_team_id == team.id
        gf = m.home_score if is_home else m.away_score
        ga = m.away_score if is_home else m.home_score
        goals_for += gf
        goals_against += ga
        if gf > ga:
            wins += 1
        elif gf < ga:
            losses += 1
        else:
            draws += 1
        opponent = m.away_team.team_name if is_home else m.home_team.team_name
        match_list.append(
            {
                "opponent": opponent,
                "score": f"{gf}-{ga}",
                "stage": m.stage.stage_name if m.stage else None,
                "date": str(m.match_date) if m.match_date else None,
            }
        )
        if m.stage:
            furthest_stage = m.stage.stage_name

    return {
        "team": team.team_name,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "furthest_stage_reached": furthest_stage,
        "matches": match_list,
    }


async def get_match_result(db: AsyncSession, team_a: str, team_b: str) -> dict:
    stmt = (
        select(Match)
        .join(Team, Match.home_team_id == Team.id)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
            selectinload(Match.stage),
            selectinload(Match.venue),
            selectinload(Match.player_of_the_match),
        )
    )
    result = await db.execute(stmt)
    all_matches = result.scalars().all()

    a_lower, b_lower = team_a.lower(), team_b.lower()
    matches = [
        m
        for m in all_matches
        if {m.home_team.team_name.lower(), m.away_team.team_name.lower()}
        >= {a_lower, b_lower}
        or (a_lower in m.home_team.team_name.lower() and b_lower in m.away_team.team_name.lower())
        or (a_lower in m.away_team.team_name.lower() and b_lower in m.home_team.team_name.lower())
    ]

    if not matches:
        return {"error": f"No match found between '{team_a}' and '{team_b}'"}

    return [
        {
            "home_team": m.home_team.team_name,
            "away_team": m.away_team.team_name,
            "score": f"{m.home_score}-{m.away_score}",
            "stage": m.stage.stage_name if m.stage else None,
            "date": str(m.match_date) if m.match_date else None,
            "venue": m.venue.stadium_name if m.venue else None,
            "player_of_the_match": m.player_of_the_match.player_name
            if m.player_of_the_match
            else None,
        }
        for m in matches
    ]


async def get_player_stats(db: AsyncSession, player_name: str) -> dict:
    stmt = (
        select(Player)
        .where(Player.player_name.ilike(f"%{player_name}%"))
        .options(selectinload(Player.team), selectinload(Player.stats))
    )
    result = await db.execute(stmt)
    player = result.scalars().first()
    if player is None:
        return {"error": f"No player found matching '{player_name}'"}

    stats = player.stats
    return {
        "player_name": player.player_name,
        "team": player.team.team_name,
        "position": player.position,
        "goals": stats.goals if stats else None,
        "assists": stats.assists if stats else None,
        "matches_played": stats.matches_played if stats else None,
        "yellow_cards": stats.yellow_cards if stats else None,
        "red_cards": stats.red_cards if stats else None,
        "average_rating": stats.average_rating if stats else None,
    }


async def get_tournament_champion(db: AsyncSession) -> dict:
    stmt = (
        select(Match)
        .join(Match.stage)
        .where(Match.stage.has(stage_name="Final"))
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
            selectinload(Match.player_of_the_match),
        )
    )
    result = await db.execute(stmt)
    final = result.scalars().first()

    if final is None or final.home_score is None or final.away_score is None:
        return {"error": "No completed Final match found in the data."}

    if final.home_penalties is not None and final.away_penalties is not None:
        champion = (
            final.home_team.team_name
            if final.home_penalties > final.away_penalties
            else final.away_team.team_name
        )
        decided_by = "penalties"
    else:
        champion = (
            final.home_team.team_name
            if final.home_score > final.away_score
            else final.away_team.team_name
        )
        decided_by = "regular play"

    runner_up = (
        final.away_team.team_name
        if champion == final.home_team.team_name
        else final.home_team.team_name
    )

    return {
        "champion": champion,
        "runner_up": runner_up,
        "score": f"{final.home_score}-{final.away_score}",
        "decided_by": decided_by,
        "date": str(final.match_date) if final.match_date else None,
        "player_of_the_match": final.player_of_the_match.player_name
        if final.player_of_the_match
        else None,
    }
