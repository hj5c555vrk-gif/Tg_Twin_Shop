from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Category


# ==================================================
# ПОЛУЧЕНИЕ ВСЕХ КАТЕГОРИЙ
# ==================================================

async def get_categories(
    session: AsyncSession
):

    result = await session.execute(

        select(Category)
        .order_by(Category.id)

    )

    return result.scalars().all()