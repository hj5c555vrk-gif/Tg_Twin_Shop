import unittest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bot.database.base import Base
from bot.database.models import MessagePhoto
from bot.services.photos import get_message_photo, set_message_photo, delete_message_photo, DEFAULT_PHOTOS


class MessagePhotoServiceTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_get_message_photo_defaults(self):
        async with self.session_factory() as session:
            # Check default fallback photo URLs
            start_photo = await get_message_photo(session, "start")
            self.assertEqual(start_photo, DEFAULT_PHOTOS["start"])

            profile_photo = await get_message_photo(session, "profile")
            self.assertEqual(profile_photo, DEFAULT_PHOTOS["profile"])

            unknown_photo = await get_message_photo(session, "non_existent_path")
            self.assertEqual(unknown_photo, "https://dummyimage.com/600x400/000000/ffffff&text=Photo")

    async def test_set_and_delete_message_photo(self):
        async with self.session_factory() as session:
            # Set a custom photo
            photo_record = await set_message_photo(session, "start", "AgACAgIAAxkBAA...")
            self.assertEqual(photo_record.path, "start")
            self.assertEqual(photo_record.photo_id, "AgACAgIAAxkBAA...")

            # Retrieve it
            retrieved_photo = await get_message_photo(session, "start")
            self.assertEqual(retrieved_photo, "AgACAgIAAxkBAA...")

            # Delete the custom photo config
            deleted = await delete_message_photo(session, "start")
            self.assertTrue(deleted)

            # Check that it falls back to default
            fallback_photo = await get_message_photo(session, "start")
            self.assertEqual(fallback_photo, DEFAULT_PHOTOS["start"])

            # Delete on non-existent path
            deleted_again = await delete_message_photo(session, "start")
            self.assertFalse(deleted_again)
