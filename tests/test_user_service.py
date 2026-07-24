import unittest

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bot.database.base import Base
from bot.database.models import User
from bot.services.user import get_or_create_user


class GetOrCreateUserTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_creates_user_and_updates_existing_profile(self):
        async with self.session_factory() as session:
            user = await get_or_create_user(session, 101, "nick", "Иван")
            self.assertEqual(user.telegram_id, 101)
            self.assertEqual(user.username, "nick")
            self.assertEqual(user.first_name, "Иван")

            updated_user = await get_or_create_user(session, 101, "new_nick", "Иван Петров")
            self.assertEqual(updated_user.id, user.id)
            self.assertEqual(updated_user.username, "new_nick")
            self.assertEqual(updated_user.first_name, "Иван Петров")

            total_count = await session.scalar(select(func.count()).select_from(User))
            self.assertEqual(total_count, 1)


if __name__ == "__main__":
    unittest.main()
