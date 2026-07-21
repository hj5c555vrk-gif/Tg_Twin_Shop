from aiogram.fsm.state import State, StatesGroup


class AddProductStates(StatesGroup):

    name = State()

    description = State()

    price = State()

    stock = State()