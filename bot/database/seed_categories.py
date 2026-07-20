from sqlalchemy import select

from bot.database.models import Category


CATEGORIES = [
    "🧃 Жидкости",
    "⚙️ Испарители",
    "🧜🏼‍♂️ Снюс",
]


async def seed_categories(session):
    for name in CATEGORIES:
        result = await session.execute(
            select(Category).where(Category.name == name)
        )

        if result.scalar() is None:
            session.add(Category(name=name))

    await session.commit()