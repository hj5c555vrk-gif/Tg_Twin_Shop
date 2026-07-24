import unittest

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bot.database.base import Base
from bot.database.models import Category, Order, User
from bot.services.user import (
    get_or_create_user,
    get_user_profile,
    increase_user_category_click,
)


class UserProfileTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def asyncTearDown(self):
        await self.engine.dispose()

    async def test_profile_returns_registration_date_favorite_categories_and_order_count(self):
        async with self.session_factory() as session:
            user = await get_or_create_user(session, 202, "profile_user", "Профиль")

            first_category = Category(name="🧃 Жидкости")
            second_category = Category(name="⚙️ Испарители")
            session.add_all([first_category, second_category])
            await session.commit()

            await increase_user_category_click(session, user.id, first_category.id)
            await increase_user_category_click(session, user.id, first_category.id)
            await increase_user_category_click(session, user.id, second_category.id)

            session.add(Order(user_id=user.id, status="completed", total_price="1.00"))
            await session.commit()

            profile = await get_user_profile(session, user.telegram_id)

            self.assertIsNotNone(profile["registered_at"])
            self.assertEqual(profile["order_count"], 1)
            self.assertEqual(profile["favorite_categories"], ["🧃 Жидкости", "⚙️ Испарители"])


if __name__ == "__main__":
    unittest.main()
