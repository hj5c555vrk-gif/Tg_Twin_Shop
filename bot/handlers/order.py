from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.database.admin import ADMIN_ID, is_admin_user
from bot.database.base import async_session
from bot.database.models import Order
from bot.keyboards.admin_key import back_to_admin_keyboard
from bot.keyboards.user_key import user_menu_keyboard
from bot.services.order import (
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_REJECTED,
    ORDER_STATUS_SENT,
    create_order_from_cart,
    get_order_with_items,
    list_orders,
    update_order_status,
)
from bot.states.order_states import OrderStates

order_router = Router()
is_admin = is_admin_user


def format_order_items(order: Order) -> str:
    lines = []

    for item in order.items:
        product_name = item.product.name if item.product else "Товар"
        line_total = float(item.price) * item.quantity
        lines.append(
            f"• {product_name}\n"
            f"  Кол-во: {item.quantity}\n"
            f"  Сумма: {line_total:.2f} ₽"
        )

    return "\n".join(lines)


def format_contact(order: Order) -> str:
    user = order.user
    username = f"@{user.username}" if user and user.username else "—"
    first_name = user.first_name or "—"
    return (
        f"ID: {user.telegram_id}\n"
        f"Пользователь: {first_name}\n"
        f"Ссылка: {username}"
    )


def build_admin_order_actions_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять заказ",
                    callback_data=f"order_accept_{order_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить заказ",
                    callback_data=f"order_reject_{order_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data="admin_orders",
                )
            ],
        ]
    )


def build_order_buttons(order: Order) -> InlineKeyboardMarkup:
    buttons = []

    if order.status == ORDER_STATUS_SENT:
        buttons.append([
            InlineKeyboardButton(
                text="✅ Принять заказ",
                callback_data=f"order_accept_{order.id}",
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                text="❌ Отклонить заказ",
                callback_data=f"order_reject_{order.id}",
            )
        ])
    elif order.status == ORDER_STATUS_IN_PROGRESS:
        buttons.append([
            InlineKeyboardButton(
                text="✅ Исполнено",
                callback_data=f"order_complete_{order.id}",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="admin_orders",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@order_router.callback_query(F.data == "checkout")
async def checkout_handler(callback: CallbackQuery):
    await callback.answer()

    async with async_session() as session:
        order = await create_order_from_cart(session, callback.from_user.id)

    if order is None:
        await callback.answer("Ваша корзина пуста или не найдена.", show_alert=True)
        return

    user_chat = callback.from_user
    text = (
        "🛍 Заказ оформлен. С вами свяжется менеджер.\n\n"
        "📌 Статус: отправлен"
    )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Назад", callback_data="user_menu")],
            ]
        ),
    )

    order_text = (
        f"<b>Новый заказ #{order.id}</b>\n\n"
        f"<b>Контакты заказчика</b>\n"
        f"{format_contact(order)}\n\n"
        f"<b>Состав заказа</b>\n"
        f"{format_order_items(order)}\n\n"
        f"🧾 Итого: {float(order.total_price):.2f} ₽\n"
        f"<b>Статус</b>: отправлен"
    )

    await callback.bot.send_message(
        ADMIN_ID,
        order_text,
        reply_markup=build_admin_order_actions_keyboard(order.id),
        parse_mode="HTML",
    )


@order_router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with async_session() as session:
        orders = await list_orders(session)

    if not orders:
        text = "<b>🛒 Заказы</b>\n\nПока нет заказов."
    else:
        lines = ["<b>🛒 Заказы</b>", ""]

        for order in orders[-10:]:
            status = order.status.replace("_", " ")
            lines.append(
                f"#{order.id} — {status}\n"
                f"Пользователь: {order.user.first_name or '—'} ({order.user.telegram_id})\n"
                f"Сумма: {float(order.total_price):.2f} ₽\n"
                f"Статус: {status}"
            )
            lines.append("")

        text = "\n".join(lines)

    await callback.answer()
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=back_to_admin_keyboard,
    )


@order_router.callback_query(F.data.startswith("order_status_"))
async def order_status(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    order_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        order = await get_order_with_items(session, order_id)

    if order is None:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    text = (
        f"<b>Заказ #{order.id}</b>\n\n"
        f"<b>Контакты</b>\n{format_contact(order)}\n\n"
        f"<b>Состав заказа</b>\n{format_order_items(order)}\n\n"
        f"🧾 Итого: {float(order.total_price):.2f} ₽\n"
        f"<b>Текущий статус</b>: {order.status.replace('_', ' ')}"
    )

    await callback.answer()
    await callback.message.edit_text(
        text,
        reply_markup=build_order_buttons(order),
        parse_mode="HTML",
    )


@order_router.callback_query(F.data.startswith("order_accept_"))
async def order_accept(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    order_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        order = await update_order_status(
            session,
            order_id,
            ORDER_STATUS_IN_PROGRESS,
        )

    if order is None:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    await callback.answer("Заказ принят в исполнение")
    await callback.message.edit_text(
        f"<b>Заказ #{order.id}</b> переведен в исполнение.",
        reply_markup=build_order_buttons(order),
        parse_mode="HTML",
    )

    await callback.bot.send_message(
        order.user.telegram_id,
        "Ваш заказ принят менеджером и находится в исполнении.",
    )


@order_router.callback_query(F.data.startswith("order_reject_"))
async def order_reject(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    order_id = int(callback.data.split("_")[2])
    await state.update_data(order_id=order_id)
    await state.set_state(OrderStates.reject_reason)

    await callback.answer()
    await callback.message.edit_text(
        "Введите причину отказа заказа:",
    )


@order_router.message(OrderStates.reject_reason)
async def reject_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("order_id")
    reason = (message.text or "").strip() or "Причина не указана."

    async with async_session() as session:
        order = await update_order_status(
            session,
            order_id,
            ORDER_STATUS_REJECTED,
            manager_comment=reason,
        )

    await state.clear()

    if order is None:
        await message.answer("Заказ не найден.")
        return

    await message.answer(
        f"Заказ #{order.id} отклонен."
    )

    await message.bot.send_message(
        order.user.telegram_id,
        (
            f"Ваш заказ #{order.id} был отклонен менеджером.\n"
            f"Причина: {reason}"
        ),
    )


@order_router.callback_query(F.data.startswith("order_complete_"))
async def order_complete(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    order_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        order = await update_order_status(
            session,
            order_id,
            ORDER_STATUS_COMPLETED,
        )

    if order is None:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    await callback.answer("Заказ отмечен как исполненный")
    await callback.message.edit_text(
        f"<b>Заказ #{order.id}</b> выполнен.",
        reply_markup=back_to_admin_keyboard,
        parse_mode="HTML",
    )

    await callback.bot.send_message(
        order.user.telegram_id,
        "Ваш заказ выполнен. Спасибо, что выбрали нас!",
    )
