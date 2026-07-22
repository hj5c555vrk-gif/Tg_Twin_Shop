from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.admin_key import admin_keyboard


common_router = Router()


@common_router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):

    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "❌ Сейчас нет активной операции."
        )
        return

    await state.clear()

    await message.answer(
        "✅ Операция отменена.\n\n"
        "Все введённые данные очищены.",
        reply_markup=admin_keyboard
    )


@common_router.message(Command("menu"))
async def menu_handler(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "📋 Главное меню.",
        reply_markup=admin_keyboard
    )


@common_router.message(Command("admin"))
async def admin_handler(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "🛠 Админ-панель.",
        reply_markup=admin_keyboard
    )


@common_router.message(Command("state"))
async def state_handler(message: Message, state: FSMContext):

    current_state = await state.get_state()

    if current_state:
        await message.answer(
            f"📍 Текущее состояние:\n\n{current_state}"
        )
    else:
        await message.answer(
            "FSM сейчас не используется."
        )


@common_router.message(Command("clear"))
async def clear_handler(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "🧹 FSM полностью очищен."
    )