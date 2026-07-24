import unittest

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bot.database.base import Base
from bot.database.models import Category, Product
from bot.database.seed_products import seed_products


class SeedProductsTests(unittest.IsolatedAsyncioTestCase):
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

    async def test_seed_products_handles_empty_catalog_without_crashing(self):
        async with self.session_factory() as session:
            await seed_products(session)

            result = await session.execute(
                __import__("sqlalchemy").select(Product)
            )
            products = result.scalars().all()
            self.assertEqual(products, [])


if __name__ == "__main__":
    unittest.main()
