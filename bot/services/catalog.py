from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Category


async def get_categories(session: AsyncSession):
    result = await session.execute(
        select(Category)
    )

    return result.scalars().all()