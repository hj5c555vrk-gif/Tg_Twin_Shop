import unittest

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bot.database.base import Base
from bot.database.models import Cart, CartItem, Category, OrderItem, Product, User
from bot.services.cart import add_product_to_cart, get_cart_summary
from bot.services.order import create_order_from_cart


class OrderServiceTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_create_order_from_cart_clears_cart_and_creates_order(self):
        async with self.session_factory() as session:
            category = Category(name="Тестовая категория")
            session.add(category)
            await session.flush()

            product = Product(
                name="Тестовый товар",
                description="desc",
                price="12.00",
                stock=10,
                available=True,
                category_id=category.id,
            )
            session.add(product)
            await session.flush()

            user = User(telegram_id=999, username="tester", first_name="Tester")
            session.add(user)
            await session.commit()

            await add_product_to_cart(session, user.telegram_id, product.id, quantity=2)

            order = await create_order_from_cart(session, user.telegram_id)

            self.assertIsNotNone(order)
            self.assertEqual(order.user_id, user.id)
            self.assertEqual(float(order.total_price), 24.0)
            self.assertEqual(order.status, "sent")
            self.assertEqual(len(order.items), 1)
            self.assertEqual(order.items[0].product_id, product.id)
            self.assertEqual(order.items[0].quantity, 2)

            summary = await get_cart_summary(session, user.telegram_id)
            self.assertEqual(summary["items_count"], 0)
            self.assertEqual(summary["quantity_total"], 0)
            self.assertEqual(summary["total_price"], 0.0)


if __name__ == "__main__":
    unittest.main()
