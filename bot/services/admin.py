from sqlalchemy import select

from bot.database.models import User
from bot.database.admin import ADMIN_ID


async def is_admin(session, telegram_id):

    result = await session.execute(
        select(User)
        .where(
            User.telegram_id == telegram_id
        )
    )

    user = result.scalar()

    if not user:
        return False

    return user.telegram_id == ADMIN_ID