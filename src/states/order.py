from aiogram.dispatcher.filters.state import StatesGroup, State


class OrderStates(StatesGroup):
    process = State()
    delivered_orders = State()
    active_orders = State()
    single_active_order = State()
    pagination_delivered_orders = State()
    single_delivered_order = State()
