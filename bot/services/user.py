from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Category, Order, User, UserCategoryClick
from bot.services.order import count_completed_orders


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


async def increase_user_category_click(
    session: AsyncSession,
    user_id: int,
    category_id: int,
):
    result = await session.execute(
        select(UserCategoryClick).where(
            UserCategoryClick.user_id == user_id,
            UserCategoryClick.category_id == category_id,
        )
    )

    click = result.scalar_one_or_none()

    if click is None:
        click = UserCategoryClick(
            user_id=user_id,
            category_id=category_id,
            clicks=1,
        )
        session.add(click)
    else:
        click.clicks += 1

    await session.commit()


async def get_user_profile(session: AsyncSession, telegram_id: int):
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        return {
            "registered_at": "—",
            "order_count": 0,
            "favorite_categories": ["Пока нет данных"],
        }

    order_count = await count_completed_orders(session, telegram_id)

    favorite_categories_result = await session.execute(
        select(Category.name)
        .join(UserCategoryClick.category)
        .where(UserCategoryClick.user_id == user.id)
        .group_by(Category.id, Category.name)
        .order_by(func.sum(UserCategoryClick.clicks).desc(), Category.name.asc())
        .limit(3)
    )

    favorite_categories = [
        category_name for (category_name,) in favorite_categories_result.all()
    ] or ["Пока нет данных"]

    return {
        "registered_at": user.created_at.strftime("%d.%m.%Y") if user.created_at else "—",
        "order_count": order_count,
        "favorite_categories": favorite_categories,
    }


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