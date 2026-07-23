from pathlib import Path
import os

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from sqlalchemy.orm import DeclarativeBase


load_dotenv()


BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "shop.db"


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{DB_PATH}"
)


# Railway PostgreSQL fix
if DATABASE_URL.startswith(
    "postgres://"
):

    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+asyncpg://",
        1
    )


elif DATABASE_URL.startswith(
    "postgresql://"
):

    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1
    )



engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)


async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)



class Base(DeclarativeBase):
    pass