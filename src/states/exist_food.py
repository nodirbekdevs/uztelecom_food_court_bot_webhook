from aiogram.dispatcher.filters.state import StatesGroup, State


class ExistFoodStates(StatesGroup):
    process = State()
    single = State()
    buy = State()
    checking = State()
