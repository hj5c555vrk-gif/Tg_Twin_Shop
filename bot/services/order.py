from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Product,
    User,
)

ORDER_STATUS_SENT = "sent"
ORDER_STATUS_IN_PROGRESS = "in_progress"
ORDER_STATUS_REJECTED = "rejected"
ORDER_STATUS_COMPLETED = "completed"


async def create_order_from_cart(
    session: AsyncSession,
    telegram_id: int,
):
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        return None

    result = await session.execute(
        select(Cart).where(Cart.user_id == user.id)
    )
    cart = result.scalar_one_or_none()

    if cart is None:
        return None

    result = await session.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
        .options(selectinload(CartItem.product))
    )
    cart_items = result.scalars().all()

    if not cart_items:
        return None

    order = Order(
        user_id=user.id,
        status=ORDER_STATUS_SENT,
        total_price=Decimal("0.00"),
    )
    session.add(order)
    await session.flush()

    total_price = Decimal("0.00")

    for cart_item in cart_items:
        product = cart_item.product
        if product is None:
            continue

        price = Decimal(str(product.price))
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=cart_item.quantity,
            price=price,
        )
        session.add(order_item)
        total_price += price * cart_item.quantity

    order.total_price = total_price.quantize(Decimal("0.01"))

    for cart_item in cart_items:
        await session.delete(cart_item)

    await session.commit()
    await session.refresh(order)

    return order


async def get_order_with_items(
    session: AsyncSession,
    order_id: int,
):
    result = await session.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.user),
        )
    )

    return result.scalar_one_or_none()


async def list_orders(
    session: AsyncSession,
):
    result = await session.execute(
        select(Order)
        .order_by(Order.created_at.asc())
        .options(
            selectinload(Order.user),
            selectinload(Order.items).selectinload(OrderItem.product),
        )
    )

    return result.scalars().all()


async def update_order_status(
    session: AsyncSession,
    order_id: int,
    status: str,
    manager_comment: str | None = None,
):
    order = await get_order_with_items(session, order_id)

    if order is None:
        return None

    order.status = status

    if manager_comment is not None:
        order.manager_comment = manager_comment

    await session.commit()
    await session.refresh(order)

    return order


async def count_completed_orders(
    session: AsyncSession,
    telegram_id: int,
):
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        return 0

    from sqlalchemy import func
    from bot.database.models import Order

    completed_result = await session.execute(
        select(func.count(Order.id)).where(
            Order.user_id == user.id,
            Order.status == ORDER_STATUS_COMPLETED,
        )
    )

    return completed_result.scalar() or 0
