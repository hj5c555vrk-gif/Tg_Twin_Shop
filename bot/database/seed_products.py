from sqlalchemy import select

from bot.database.models import (
    Category,
    Product,
)

async def seed_products(session):

    for item in PRODUCTS:

        category_result = await session.execute(
            select(Category).where(
                Category.name == item["category"]
            )
        )

        category = category_result.scalar_one_or_none()

        if category is None:
            continue

        existing_result = await session.execute(
            select(Product).where(
                Product.name == item["name"],
                Product.category_id == category.id,
            )
        )

        if existing_result.scalar_one_or_none():
            continue

        session.add(
            Product(
                name=item["name"],
                description=item["description"],
                price=item["price"],
                image=item["image"],
                category_id=category.id,
                stock=0,
                available=False,
            )
        )

    await session.commit()