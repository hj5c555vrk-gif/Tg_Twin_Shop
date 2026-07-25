from sqlalchemy import select

from bot.database.models import (
    Category,
    Product,
)

DEFAULT_PRODUCTS = []


async def seed_products(session):
    product_items = globals().get("PRODUCTS", DEFAULT_PRODUCTS)

    if not product_items:
        await session.commit()
        return

    for item in product_items:
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
                available=True,
            )
        )

    await session.commit()