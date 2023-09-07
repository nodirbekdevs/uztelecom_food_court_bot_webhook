from aiogram.dispatcher.filters.state import StatesGroup, State


class RegisterStates(StatesGroup):
    language = State()
    phone = State()
    verification_code = State()
