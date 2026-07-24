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
        changed = False

        if username is not None and user.username != username:
            user.username = username
            changed = True

        if first_name is not None and user.first_name != first_name:
            user.first_name = first_name
            changed = True

        if changed:
            await session.commit()

        return user

    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name
    )

    session.add(user)

    await session.commit()

    return user


async def get_user_logs(session: AsyncSession):
    result = await session.execute(
        select(User)
        .order_by(User.created_at.asc(), User.telegram_id.asc())
    )

    users = result.scalars().all()

    return [
        {
            "telegram_id": user.telegram_id,
            "username": user.username or "—",
            "first_name": user.first_name or "—",
            "created_at": user.created_at.strftime("%d.%m.%Y %H:%M:%S") if user.created_at else "—",
        }
        for user in users
    ]