from sqlalchemy import select

from bot.database.models import Category


CATEGORIES = [
    "🧃 Жидкости",
    "⚙️ Испарители",
    "🧜🏼‍♂️ Снюс",
]


async def seed_categories(session):
    # Check if we have any categories in the database
    result = await session.execute(select(Category))
    if not result.scalars().first():
        for name in CATEGORIES:
            session.add(Category(name=name))
        await session.commit()
