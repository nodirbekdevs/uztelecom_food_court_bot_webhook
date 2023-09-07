from aiogram.dispatcher.filters.state import StatesGroup, State


class FoodStates(StatesGroup):
    process = State()
    single = State()
    order = State()
    exist = State()
    exception = State()
