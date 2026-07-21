from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str | None
):

    result = await session.execute(
        select(User)
        .where(
            User.telegram_id == telegram_id
        )
    )

    user = result.scalar()

    if user:
        return user


    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name
    )

    session.add(user)

    await session.commit()

    return user