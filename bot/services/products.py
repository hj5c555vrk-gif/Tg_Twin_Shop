from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Product


# ==================================================
# ПОЛУЧЕНИЕ ТОВАРОВ ПО КАТЕГОРИИ
# ==================================================

async def get_products_by_category(
    session: AsyncSession,
    category_id: int
):

    result = await session.execute(
        select(Product).where(
            Product.category_id == category_id
        )
    )

    return result.scalars().all()


# ==================================================
# СОЗДАНИЕ ТОВАРА
# ==================================================

async def create_product(
    session: AsyncSession,
    name: str,
    description: str,
    category_id: int,
    price: float,
    stock: int
):

    product = Product(

        name=name,

        description=description,

        category_id=category_id,

        price=price,

        stock=stock,

        available=True

    )

    session.add(product)

    await session.commit()

    await session.refresh(product)

    return product


# ==================================================
# ВСЕ ТОВАРЫ
# ==================================================

async def get_all_products(
    session: AsyncSession
):

    result = await session.execute(

        select(Product).order_by(Product.id)

    )

    return result.scalars().all()


# ==================================================
# ТОВАР ПО ID
# ==================================================

async def get_product_by_id(
    session: AsyncSession,
    product_id: int
):

    result = await session.execute(

        select(Product).where(
            Product.id == product_id
        )

    )

    return result.scalar_one_or_none()


# ==================================================
# ИЗМЕНЕНИЕ НАЗВАНИЯ
# ==================================================

async def update_product_name(
    session: AsyncSession,
    product_id: int,
    name: str
):

    product = await get_product_by_id(
        session,
        product_id
    )

    if product is None:
        return None

    product.name = name

    await session.commit()

    await session.refresh(product)

    return product


# ==================================================
# ИЗМЕНЕНИЕ ОПИСАНИЯ
# ==================================================

async def update_product_description(
    session: AsyncSession,
    product_id: int,
    description: str
):

    product = await get_product_by_id(
        session,
        product_id
    )

    if product is None:
        return None

    product.description = description

    await session.commit()

    await session.refresh(product)

    return product


# ==================================================
# ИЗМЕНЕНИЕ ЦЕНЫ
# ==================================================

async def update_product_price(
    session: AsyncSession,
    product_id: int,
    price: float
):

    product = await get_product_by_id(
        session,
        product_id
    )

    if product is None:
        return None

    product.price = price

    await session.commit()

    await session.refresh(product)

    return product


# ==================================================
# ИЗМЕНЕНИЕ ОСТАТКА
# ==================================================

async def update_stock(
    session: AsyncSession,
    product_id: int,
    stock: int
):

    product = await get_product_by_id(
        session,
        product_id
    )

    if product is None:
        return None

    product.stock = stock

    product.available = stock > 0

    await session.commit()

    await session.refresh(product)

    return product


# Совместимость со старым названием функции

async def update_product_stock(
    session: AsyncSession,
    product_id: int,
    stock: int
):
    return await update_stock(
        session,
        product_id,
        stock
    )


# ==================================================
# УДАЛЕНИЕ ТОВАРА
# ==================================================

async def delete_product(
    session: AsyncSession,
    product_id: int
):

    product = await get_product_by_id(
        session,
        product_id
    )

    if product is None:
        return False

    await session.delete(product)

    await session.commit()

    return True


# ==================================================
# ПЕРЕКЛЮЧЕНИЕ ДОСТУПНОСТИ
# ==================================================

async def set_product_available(
    session: AsyncSession,
    product_id: int,
    available: bool
):

    product = await get_product_by_id(
        session,
        product_id
    )

    if product is None:
        return None

    product.available = available

    await session.commit()

    await session.refresh(product)

    return product


# ==================================================
# ПОИСК ПО НАЗВАНИЮ
# ==================================================

async def search_products(
    session: AsyncSession,
    text: str
):

    result = await session.execute(

        select(Product).where(
            Product.name.ilike(f"%{text}%")
        )

    )

    return result.scalars().all()