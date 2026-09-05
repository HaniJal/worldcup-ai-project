from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data.sql_models import Match


async def list_matches(
    db: AsyncSession,
    stage_id: UUID | None = None,
    team_id: UUID | None = None,
) -> list[Match]:
    stmt = (
        select(Match)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
            selectinload(Match.stage),
            selectinload(Match.venue),
        )
        .order_by(Match.match_date, Match.kickoff_time)
    )
    if stage_id:
        stmt = stmt.where(Match.stage_id == stage_id)
    if team_id:
        stmt = stmt.where(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_match(db: AsyncSession, match_id: UUID) -> Match | None:
    stmt = (
        select(Match)
        .where(Match.id == match_id)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
            selectinload(Match.stage),
            selectinload(Match.venue),
            selectinload(Match.referee),
            selectinload(Match.events),
            selectinload(Match.team_stats),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
