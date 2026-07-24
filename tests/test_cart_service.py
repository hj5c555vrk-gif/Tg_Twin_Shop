import unittest

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bot.database.base import Base
from bot.database.models import Category, Product, User
from bot.services.cart import add_product_to_cart, clear_cart, get_cart_summary


class CartServiceTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_add_product_to_cart_aggregates_quantity_and_total(self):
        async with self.session_factory() as session:
            category = Category(name="Тестовая категория")
            session.add(category)
            await session.flush()

            product = Product(
                name="Тестовый товар",
                description="desc",
                price="10.50",
                stock=10,
                available=True,
                category_id=category.id,
            )
            session.add(product)
            await session.flush()

            user = User(telegram_id=777, username="tester", first_name="Tester")
            session.add(user)
            await session.commit()

            await add_product_to_cart(session, user.telegram_id, product.id, quantity=2)
            await add_product_to_cart(session, user.telegram_id, product.id, quantity=1)

            summary = await get_cart_summary(session, user.telegram_id)

            self.assertEqual(summary["items_count"], 1)
            self.assertEqual(summary["quantity_total"], 3)
            self.assertEqual(summary["total_price"], 31.5)

    async def test_clear_cart_removes_all_items(self):
        async with self.session_factory() as session:
            category = Category(name="Тестовая категория")
            session.add(category)
            await session.flush()

            product = Product(
                name="Тестовый товар",
                description="desc",
                price="5.00",
                stock=5,
                available=True,
                category_id=category.id,
            )
            session.add(product)
            await session.flush()

            user = User(telegram_id=888, username="tester2", first_name="Tester2")
            session.add(user)
            await session.commit()

            await add_product_to_cart(session, user.telegram_id, product.id, quantity=1)
            await clear_cart(session, user.telegram_id)

            summary = await get_cart_summary(session, user.telegram_id)

            self.assertEqual(summary["items_count"], 0)
            self.assertEqual(summary["quantity_total"], 0)
            self.assertEqual(summary["total_price"], 0.0)


if __name__ == "__main__":
    unittest.main()
