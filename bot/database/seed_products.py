from sqlalchemy import select

from bot.database.models import (
    Category,
    Product,
)


PRODUCTS = [
    {
        "name": "Blueberry Ice",
        "description": "Ягодный вкус с холодком",
        "price": 350,
        "image": None,
        "category": "🧃 Жидкости",
    },
    {
        "name": "Mango Ice",
        "description": "Манго с освежающим эффектом",
        "price": 350,
        "image": None,
        "category": "🧃 Жидкости",
    },
    {
        "name": "Strawberry Mix",
        "description": "Клубничный микс",
        "price": 350,
        "image": None,
        "category": "🧃 Жидкости",
    },
    {
        "name": "Испаритель 0.6Ω",
        "description": "Сетка для мощной передачи вкуса",
        "price": 250,
        "image": None,
        "category": "⚙️ Испарители",
    },
    {
        "name": "Испаритель 1.2Ω",
        "description": "Экономичный вариант для MTL затяжки",
        "price": 250,
        "image": None,
        "category": "⚙️ Испарители",
    },
    {
        "name": "Classic Mint",
        "description": "Мятный вкус",
        "price": 300,
        "image": None,
        "category": "🧜🏼‍♂️ Снюс",
    },
]


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