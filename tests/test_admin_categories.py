import unittest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from bot.database.base import Base
from bot.database.models import Category
from bot.handlers.admin import (
    admin_categories,
    admin_add_category,
    admin_save_category,
    admin_edit_categories,
    admin_edit_cat_name,
    admin_save_edited_category,
    admin_delete_categories,
    admin_delete_cat_handler,
)


class AdminCategoriesTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Create an in-memory SQLite database
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Patch async_session to return our in-memory session factory
        self.session_patcher = patch("bot.handlers.admin.async_session", self.session_factory)
        self.session_patcher.start()

        # Patch is_admin to always return True for our tests
        self.admin_patcher = patch("bot.handlers.admin.is_admin", return_value=True)
        self.admin_patcher.start()

    async def asyncTearDown(self):
        self.session_patcher.stop()
        self.admin_patcher.stop()
        await self.engine.dispose()

    async def test_admin_categories_renders_submenu(self):
        callback = AsyncMock()
        callback.from_user.id = 12345
        callback.message.edit_text = AsyncMock()

        state = AsyncMock()

        await admin_categories(callback, state)

        state.clear.assert_called_once()
        callback.answer.assert_called_once()
        callback.message.edit_text.assert_called_once()
        args, kwargs = callback.message.edit_text.call_args
        text = args[0] if args else kwargs.get("text", "")
        self.assertIn("Управление категориями", text)

    async def test_admin_add_category_sets_state(self):
        callback = AsyncMock()
        callback.from_user.id = 12345
        callback.message.edit_text = AsyncMock()

        state = AsyncMock()

        await admin_add_category(callback, state)

        state.clear.assert_called_once()
        callback.message.edit_text.assert_called_once()
        state.set_state.assert_called_once()

    async def test_admin_save_category_creates_category(self):
        message = AsyncMock()
        message.from_user.id = 12345
        message.text = "Тестовая Категория"
        message.answer = AsyncMock()

        state = AsyncMock()

        await admin_save_category(message, state)

        state.clear.assert_called_once()
        message.answer.assert_called_once()

        # Check that the category was actually created in DB
        async with self.session_factory() as session:
            result = await session.execute(select(Category).where(Category.name == "Тестовая Категория"))
            category = result.scalar_one_or_none()
            self.assertIsNotNone(category)
            self.assertEqual(category.name, "Тестовая Категория")

    async def test_admin_edit_categories_lists_categories(self):
        # Insert a category first
        async with self.session_factory() as session:
            session.add(Category(name="Кат 1"))
            session.add(Category(name="Кат 2"))
            await session.commit()

        callback = AsyncMock()
        callback.from_user.id = 12345
        callback.message.edit_text = AsyncMock()

        state = AsyncMock()

        await admin_edit_categories(callback, state)

        callback.message.edit_text.assert_called_once()
        args, kwargs = callback.message.edit_text.call_args
        text = args[0] if args else kwargs.get("text", "")
        self.assertIn("Выберите категорию для изменения названия", text)

        # Check that buttons exist
        inline_keyboard = kwargs.get("reply_markup").inline_keyboard if "reply_markup" in kwargs else args[1].inline_keyboard
        self.assertEqual(len(inline_keyboard), 3)  # 2 categories + 1 back button
        self.assertEqual(inline_keyboard[0][0].text, "✏️ Кат 1")

    async def test_admin_edit_cat_name_sets_state(self):
        async with self.session_factory() as session:
            cat = Category(name="Редакт меня")
            session.add(cat)
            await session.commit()
            cat_id = cat.id

        callback = AsyncMock()
        callback.from_user.id = 12345
        callback.data = f"admin_edit_cat_{cat_id}"
        callback.message.edit_text = AsyncMock()

        state = AsyncMock()

        await admin_edit_cat_name(callback, state)

        state.update_data.assert_called_with(category_id=cat_id)
        state.set_state.assert_called_once()
        callback.message.edit_text.assert_called_once()
        args, kwargs = callback.message.edit_text.call_args
        text = args[0] if args else kwargs.get("text", "")
        self.assertIn("Редактирование категории", text)
        self.assertIn("Редакт меня", text)

    async def test_admin_save_edited_category_saves_changes(self):
        async with self.session_factory() as session:
            cat = Category(name="Старое Имя")
            session.add(cat)
            await session.commit()
            cat_id = cat.id

        message = AsyncMock()
        message.from_user.id = 12345
        message.text = "Новое Имя"
        message.answer = AsyncMock()

        state = AsyncMock()
        state.get_data = AsyncMock(return_value={"category_id": cat_id})

        await admin_save_edited_category(message, state)

        state.clear.assert_called_once()
        message.answer.assert_called_once()

        # Verify the change in DB
        async with self.session_factory() as session:
            result = await session.execute(select(Category).where(Category.id == cat_id))
            category = result.scalar_one_or_none()
            self.assertEqual(category.name, "Новое Имя")

    async def test_admin_delete_cat_handler_deletes_category(self):
        async with self.session_factory() as session:
            cat = Category(name="Удалить Меня")
            session.add(cat)
            await session.commit()
            cat_id = cat.id

        callback = AsyncMock()
        callback.from_user.id = 12345
        callback.data = f"admin_delete_cat_{cat_id}"
        callback.message.edit_text = AsyncMock()

        state = AsyncMock()

        await admin_delete_cat_handler(callback, state)

        # Check that callback.answer was called with "Категория удалена"
        any_match = any(
            args and args[0] == "Категория удалена"
            for args, kwargs in callback.answer.call_args_list
        )
        self.assertTrue(any_match)

        # Verify it was deleted from DB
        async with self.session_factory() as session:
            result = await session.execute(select(Category).where(Category.id == cat_id))
            category = result.scalar_one_or_none()
            self.assertIsNone(category)


if __name__ == "__main__":
    unittest.main()
