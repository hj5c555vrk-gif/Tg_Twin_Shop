from aiogram.fsm.state import State, StatesGroup


class AddProductStates(StatesGroup):

    # Добавление товара

    name = State()

    description = State()

    category = State()

    price = State()

    stock = State()


    # Редактирование товара

    edit_name = State()

    edit_description = State()

    edit_price = State()

    edit_stock = State()