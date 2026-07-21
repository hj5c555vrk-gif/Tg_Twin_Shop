from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Product



# Получение товаров по категории

async def get_products_by_category(
    session: AsyncSession,
    category_id: int
):

    result = await session.execute(

        select(Product)
        .where(
            Product.category_id == category_id
        )

    )

    return result.scalars().all()



# Создание нового товара

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

        stock=stock

    )


    session.add(product)


    await session.commit()


    await session.refresh(product)


    return product



# Получение всех товаров

async def get_all_products(
    session: AsyncSession
):

    result = await session.execute(

        select(Product)

    )

    return result.scalars().all()



# Получение товара по ID

async def get_product_by_id(
    session: AsyncSession,
    product_id: int
):

    result = await session.execute(

        select(Product)
        .where(
            Product.id == product_id
        )

    )


    return result.scalar_one_or_none()



# Изменение остатка товара

async def update_product_stock(
    session: AsyncSession,
    product_id: int,
    stock: int
):

    product = await get_product_by_id(
        session,
        product_id
    )


    if not product:
        return None


    product.stock = stock


    await session.commit()


    await session.refresh(product)


    return product