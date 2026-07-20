from bot.database.models import Category


async def get_categories(session):
    result = await session.execute(select(Category))
    return result.scalars().all()