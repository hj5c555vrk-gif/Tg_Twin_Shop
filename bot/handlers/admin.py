from aiogram import Router
from aiogram.types import Message


admin_router = Router()


print("ADMIN ROUTER LOADED")


@admin_router.message()
async def admin_test(message: Message):

    print(
        "MESSAGE RECEIVED:",
        message.text
    )

    await message.answer(
        "ADMIN ROUTER WORKS"
    )