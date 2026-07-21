from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.base import async_session
from bot.services.catalog import get_categories
from bot.keyboards.catalog_key import catalog_keyboard
from bot.services.user import get_or_create_user
from bot.database.models import User

user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: Message):

    async with async_session() as session:

        result = await session.execute(
            select(User)
            .where(
                User.telegram_id ==
                message.from_user.id
            )
        )

        user = result.scalar()


        if not user:

            new_user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )

            session.add(new_user)

            await session.commit()


    await message.answer(
        "Добро пожаловать в магазин!"
    )