from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data.sql_models import Team


async def list_teams(db: AsyncSession, group_letter: str | None = None) -> list[Team]:
    stmt = select(Team).order_by(Team.group_letter, Team.team_name)
    if group_letter:
        stmt = stmt.where(Team.group_letter == group_letter.upper())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_team(db: AsyncSession, team_id: UUID) -> Team | None:
    stmt = (
        select(Team)
        .where(Team.id == team_id)
        .options(selectinload(Team.players))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
