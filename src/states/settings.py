from aiogram.dispatcher.filters.state import StatesGroup, State


class SettingStates(StatesGroup):
    process = State()
    phone = State()
    language = State()
