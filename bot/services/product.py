from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Product


async def get_products_by_category(
    session: AsyncSession,
    category_id: int
):
    result = await session.execute(
        select(Product).where(Product.category_id == category_id)
    )

    return result.scalars().all()
    
async def create_product(
    session: AsyncSession,
    name: str,
    description: str,
    price: int,
    stock: int
):

    product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock
    )

    session.add(product)

    await session.commit()

    await session.refresh(product)

    return product