"""
Turn structured DB rows into short natural-language text chunks suitable for
embedding and retrieval. Each function returns a list of (text, metadata)
pairs — metadata is stored alongside the vector in Qdrant so retrieved
results can be traced back to their source record (and later joined back to
the relational DB if needed).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data.sql_models import Match, MatchEvent, Player, PlayerStats, Team

Chunk = tuple[str, dict]


def _match_text(match: Match) -> str:
    home = match.home_team.team_name
    away = match.away_team.team_name
    stage = match.stage.stage_name if match.stage else "Unknown stage"
    venue = f" at {match.venue.stadium_name}, {match.venue.city}" if match.venue else ""
    date_str = f" on {match.match_date}" if match.match_date else ""

    if match.home_score is None or match.away_score is None:
        result = f"{home} vs {away} has not been played yet."
    else:
        if match.home_score > match.away_score:
            result = f"{home} beat {away} {match.home_score}-{match.away_score}"
        elif match.away_score > match.home_score:
            result = f"{away} beat {home} {match.away_score}-{match.home_score}"
        else:
            result = f"{home} and {away} drew {match.home_score}-{match.away_score}"

        if match.home_penalties is not None and match.away_penalties is not None:
            result += (
                f" ({home} {match.home_penalties}-{match.away_penalties} {away} on penalties)"
            )

    potm = ""
    if match.player_of_the_match is not None:
        potm = f" {match.player_of_the_match.player_name} was named Player of the Match."

    xg = ""
    if match.home_xg is not None and match.away_xg is not None:
        xg = f" Expected goals (xG): {home} {match.home_xg:.2f}, {away} {match.away_xg:.2f}."

    event_lines = []
    for event in sorted(match.events, key=lambda e: (e.minute or 0)):
        if event.player is not None and event.event_type:
            minute = f"{event.minute}'" if event.minute is not None else ""
            event_lines.append(f"{minute} {event.event_type} - {event.player.player_name}")
    events_text = ""
    if event_lines:
        events_text = " Key events: " + "; ".join(event_lines) + "."

    text = (
        f"{stage} match{date_str}{venue}: {result}.{potm}{xg}{events_text}"
    )
    return text


async def build_match_chunks(db: AsyncSession) -> list[Chunk]:
    stmt = select(Match).options(
        selectinload(Match.home_team),
        selectinload(Match.away_team),
        selectinload(Match.stage),
        selectinload(Match.venue),
        selectinload(Match.player_of_the_match),
        selectinload(Match.events).selectinload(MatchEvent.player),
    )
    result = await db.execute(stmt)
    matches = result.scalars().all()

    chunks: list[Chunk] = []
    for match in matches:
        text = _match_text(match)
        metadata = {
            "type": "match",
            "match_id": str(match.id),
            "home_team": match.home_team.team_name,
            "away_team": match.away_team.team_name,
            "stage": match.stage.stage_name if match.stage else None,
            "match_date": str(match.match_date) if match.match_date else None,
        }
        chunks.append((text, metadata))
    return chunks


def _player_text(player: Player, stats: PlayerStats | None) -> str:
    team = player.team.team_name
    position = player.position or "player"
    club = f", plays club football at {player.club_team}" if player.club_team else ""
    age_info = ""
    if player.date_of_birth:
        age_info = f", born {player.date_of_birth}"

    base = f"{player.player_name} is a {position} for {team}{age_info}{club}."

    if stats is None:
        return base

    stat_parts = []
    if stats.matches_played:
        stat_parts.append(f"played {stats.matches_played} matches")
    if stats.goals:
        stat_parts.append(f"scored {stats.goals} goals")
    if stats.assists:
        stat_parts.append(f"provided {stats.assists} assists")
    if stats.yellow_cards:
        stat_parts.append(f"received {stats.yellow_cards} yellow cards")
    if stats.red_cards:
        stat_parts.append(f"received {stats.red_cards} red cards")
    if stats.saves:
        stat_parts.append(f"made {stats.saves} saves")
    if stats.clean_sheets:
        stat_parts.append(f"kept {stats.clean_sheets} clean sheets")
    if stats.average_rating:
        stat_parts.append(f"averaged a {stats.average_rating:.1f} match rating")

    if not stat_parts:
        return base

    stats_text = "In the 2026 World Cup, they " + ", ".join(stat_parts) + "."
    return f"{base} {stats_text}"


async def build_player_chunks(db: AsyncSession) -> list[Chunk]:
    stmt = select(Player).options(selectinload(Player.team), selectinload(Player.stats))
    result = await db.execute(stmt)
    players = result.scalars().all()

    chunks: list[Chunk] = []
    for player in players:
        stats = player.stats
        text = _player_text(player, stats)
        metadata = {
            "type": "player",
            "player_id": str(player.id),
            "player_name": player.player_name,
            "team": player.team.team_name,
            "position": player.position,
        }
        chunks.append((text, metadata))
    return chunks


def _team_text(team: Team) -> str:
    parts = [
        f"{team.team_name} ({team.fifa_code}) competed in Group {team.group_letter}"
        f" of the {team.confederation} confederation."
    ]
    if team.fifa_ranking:
        parts.append(f"Pre-tournament FIFA ranking: {team.fifa_ranking}.")
    if team.elo_rating:
        parts.append(f"Elo rating: {team.elo_rating:.0f}.")
    if team.manager_name:
        parts.append(f"Managed by {team.manager_name}.")
    return " ".join(parts)


async def build_team_chunks(db: AsyncSession) -> list[Chunk]:
    stmt = select(Team)
    result = await db.execute(stmt)
    teams = result.scalars().all()

    chunks: list[Chunk] = []
    for team in teams:
        text = _team_text(team)
        metadata = {
            "type": "team",
            "team_id": str(team.id),
            "team_name": team.team_name,
            "group_letter": team.group_letter,
        }
        chunks.append((text, metadata))
    return chunks


async def build_all_chunks(db: AsyncSession) -> list[Chunk]:
    chunks: list[Chunk] = []
    chunks += await build_team_chunks(db)
    chunks += await build_player_chunks(db)
    chunks += await build_match_chunks(db)
    return chunks
