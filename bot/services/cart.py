from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.models import (
    User,
    Cart,
    CartItem,
    Product,
)


async def get_or_create_cart(
    session: AsyncSession,
    telegram_id: int
):

    result = await session.execute(
        select(User)
        .where(
            User.telegram_id == telegram_id
        )
    )

    user = result.scalar()


    if not user:
        return None


    result = await session.execute(
        select(Cart)
        .where(
            Cart.user_id == user.id
        )
    )

    cart = result.scalar()


    if cart:
        return cart


    cart = Cart(
        user_id=user.id
    )

    session.add(cart)

    await session.commit()

    return cart


async def add_product_to_cart(
    session: AsyncSession,
    telegram_id: int,
    product_id: int,
    quantity: int = 1,
):
    cart = await get_or_create_cart(session, telegram_id)

    if cart is None:
        return None

    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if product is None:
        return None

    result = await session.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
        )
    )
    item = result.scalar_one_or_none()

    if item is None:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        session.add(item)
    else:
        item.quantity += quantity

    await session.commit()
    await session.refresh(item)
    return item


async def get_cart_summary(session: AsyncSession, telegram_id: int):
    cart = await get_or_create_cart(session, telegram_id)

    if cart is None:
        return {
            "items": [],
            "items_count": 0,
            "quantity_total": 0,
            "total_price": 0.0,
        }

    result = await session.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
        .options(selectinload(CartItem.product))
    )
    items_db = result.scalars().all()

    items = []
    quantity_total = 0
    total_price = Decimal("0.00")

    for item in items_db:
        quantity_total += item.quantity
        total_price += Decimal(str(item.product.price)) * item.quantity
        items.append(
            {
                "id": item.product.id,
                "name": item.product.name,
                "quantity": item.quantity,
                "price": float(Decimal(str(item.product.price))),
                "line_total": float(Decimal(str(item.product.price)) * item.quantity),
            }
        )

    return {
        "items": items,
        "items_count": len(items),
        "quantity_total": quantity_total,
        "total_price": float(total_price.quantize(Decimal("0.01"))),
    }


async def clear_cart(session: AsyncSession, telegram_id: int):
    cart = await get_or_create_cart(session, telegram_id)

    if cart is None:
        return False

    result = await session.execute(
        select(CartItem).where(CartItem.cart_id == cart.id)
    )
    items = result.scalars().all()

    for item in items:
        await session.delete(item)

    await session.commit()
    return True