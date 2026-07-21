from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import (
    User,
    Cart,
    CartItem
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