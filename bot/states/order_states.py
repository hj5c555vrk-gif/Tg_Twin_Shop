from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    reject_reason = State()
