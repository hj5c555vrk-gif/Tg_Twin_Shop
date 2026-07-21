from datetime import datetime, timedelta

from sqlalchemy import select, func

from bot.database.models import User, Category


async def get_users_count(session):

    result = await session.execute(
        select(func.count(User.id))
    )

    return result.scalar()


async def get_new_users(session, days):

    date = datetime.utcnow() - timedelta(days=days)

    result = await session.execute(
        select(func.count(User.id))
        .where(User.created_at >= date)
    )

    return result.scalar()


async def get_popular_category(session):

    result = await session.execute(
        select(
            Category.name,
            CategoryView.views
        )
        .join(
            CategoryView.category
        )
        .order_by(
            CategoryView.views.desc()
        )
    )


    category = result.first()


    if category:
        return (
            f"{category[0]} "
            f"({category[1]} просмотров)"
        )


    return "Нет данных"


async def get_analytics(session):

    total = await get_users_count(session)

    day = await get_new_users(
        session,
        1
    )

    week = await get_new_users(
        session,
        7
    )

    month = await get_new_users(
        session,
        30
    )

    popular = await get_popular_category(
        session
    )

    return {
        "total": total,
        "day": day,
        "week": week,
        "month": month,
        "popular": popular
    }