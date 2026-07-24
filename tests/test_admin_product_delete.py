import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from bot.handlers.admin import delete_product_menu


class AdminProductDeleteTests(unittest.IsolatedAsyncioTestCase):
    async def test_delete_product_menu_lists_products_for_removal(self):
        callback = Mock()
        callback.data = "delete_product"
        callback.from_user.id = 1
        callback.answer = AsyncMock()
        callback.message.edit_text = AsyncMock()

        fake_products = [
            SimpleNamespace(id=7, name="Тестовый товар", price=99.99, stock=3),
        ]

        class FakeSessionContext:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

        async def fake_get_all_products(session):
            return fake_products

        with patch("bot.handlers.admin.is_admin", return_value=True), \
             patch("bot.handlers.admin.get_all_products", side_effect=fake_get_all_products), \
             patch("bot.handlers.admin.async_session", return_value=FakeSessionContext()):
            await delete_product_menu(callback)

        callback.answer.assert_awaited_once()
        callback.message.edit_text.assert_awaited_once()

        _, kwargs = callback.message.edit_text.await_args
        self.assertIn("Выберите товар для удаления", kwargs["text"])
        self.assertEqual(
            kwargs["reply_markup"].inline_keyboard[0][0].callback_data,
            "delete_7",
        )


if __name__ == "__main__":
    unittest.main()
