from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import (
    Product,
    Category,
)


async def get_products_by_category(
    session: AsyncSession,
    category_id: int
):

    result = await session.execute(
        select(Product)
        .where(
            Product.category_id == category_id
        )
        .order_by(
            Product.id
        )
    )

    return result.scalars().all()



async def create_product(
    session: AsyncSession,
    name: str,
    description: str,
    category_id: int,
    price: float,
    stock: int
):

    category_result = await session.execute(
        select(Category)
        .where(
            Category.id == category_id
        )
    )

    category = category_result.scalar_one_or_none()


    if category is None:
        return None


    product = Product(

        name=name,

        description=description,

        category_id=category_id,

        price=price,

        stock=stock,

        available=stock > 0

    )


    try:

        session.add(product)

        await session.commit()

        await session.refresh(product)

        return product


    except Exception:

        await session.rollback()

        raise



async def get_all_products(
    session: AsyncSession
):

    result = await session.execute(

        select(Product)
        .order_by(
            Product.id
        )

    )

    return result.scalars().all()



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


    try:

        await session.commit()

        await session.refresh(product)

        return product


    except Exception:

        await session.rollback()

        raise



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


    try:

        await session.commit()

        await session.refresh(product)

        return product


    except Exception:

        await session.rollback()

        raise



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


    try:

        await session.commit()

        await session.refresh(product)

        return product


    except Exception:

        await session.rollback()

        raise



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


    try:

        await session.commit()

        await session.refresh(product)

        return product


    except Exception:

        await session.rollback()

        raise



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


    try:

        await session.delete(product)

        await session.commit()

        return True


    except Exception:

        await session.rollback()

        raise



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


    try:

        await session.commit()

        await session.refresh(product)

        return product


    except Exception:

        await session.rollback()

        raise



async def search_products(
    session: AsyncSession,
    text: str
):

    result = await session.execute(

        select(Product)
        .where(
            Product.name.ilike(
                f"%{text}%"
            )
        )

    )

    return result.scalars().all()