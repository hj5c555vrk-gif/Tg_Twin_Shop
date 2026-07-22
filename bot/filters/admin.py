from aiogram.filters import BaseFilter
from aiogram.types import Message

import os
from dotenv import load_dotenv

load_dotenv()


ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")


class AdminFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:

        user_id = str(message.from_user.id)

        return user_id in ADMIN_IDS