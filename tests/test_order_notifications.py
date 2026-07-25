import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bot.database.admin import ADMIN_ID
from bot.handlers.order import build_admin_order_actions_keyboard
from bot.handlers.menu import get_menu_markup
from bot.keyboards.admin_key import admin_keyboard
from bot.keyboards.user_key import user_menu_keyboard


def test_admin_order_notification_keyboard_contains_expected_actions():
    keyboard = build_admin_order_actions_keyboard(42)

    buttons = [button.text for row in keyboard.inline_keyboard for button in row]
    callback_map = {
        button.text: button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
    }

    assert "✅ Принять заказ" in buttons
    assert "❌ Отменить заказ" in buttons
    assert "◀️ Назад" in buttons
    assert callback_map["✅ Принять заказ"] == "order_accept_42"
    assert callback_map["❌ Отменить заказ"] == "order_reject_42"
    assert callback_map["◀️ Назад"] == "admin_orders"


def test_menu_markup_uses_admin_keyboard_for_admin_users():
    assert get_menu_markup(ADMIN_ID) == admin_keyboard
    assert get_menu_markup(100) == user_menu_keyboard
