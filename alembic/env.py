from logging.config import fileConfig

import asyncio
import os
import sys

from dotenv import load_dotenv

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context


load_dotenv()


sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)


config = context.config


database_url = os.getenv(
    "DATABASE_URL"
)


if database_url:

    if database_url.startswith(
        "postgresql://"
    ):

        database_url = database_url.replace(
            "postgresql://",
            "postgresql+asyncpg://",
            1
        )

    config.set_main_option(
        "sqlalchemy.url",
        database_url
    )


if config.config_file_name is not None:

    fileConfig(
        config.config_file_name
    )


from bot.database.models import Base


target_metadata = Base.metadata



def run_migrations_offline() -> None:

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():

        context.run_migrations()



async def run_async_migrations():

    connectable = async_engine_from_config(

        config.get_section(
            config.config_ini_section,
            {}
        ),

        prefix="sqlalchemy.",

        poolclass=pool.NullPool,

    )


    async with connectable.connect() as connection:


        await connection.run_sync(

            lambda sync_connection:

            context.configure(

                connection=sync_connection,

                target_metadata=target_metadata,

            )

        )


        await connection.run_sync(

            lambda sync_connection:

            context.run_migrations()

        )


    await connectable.dispose()



def run_migrations_online() -> None:

    asyncio.run(
        run_async_migrations()
    )



if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()