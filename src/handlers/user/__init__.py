from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from src.loader import dp, storage
from src.helpers.utils import translator
from src.helpers.keyboard_buttons import option
from src.helpers.format import main_page_format
from src.keyboards.user import menu_keyboard
from src.handlers.user.register import cmd_start
from src.states.order import OrderStates
from src.states.food import FoodStates
from src.states.basket import BasketStates
from src.states.settings import SettingStates
from src.states.user import UserStates


# @dp.message_handler(text=[option['main']['uz'], option['main']['ru']])
# async def main_page_handler():
#
#     pass


async def back_to_main_menu_handler(send, state: FSMContext):
    message = dict()

    async with state.proxy() as data:
        language = data.get(f'{send.from_user.id}_user_language')

    if type(send) is Message:
        message = send
    elif type(send) is CallbackQuery:
        message = send.message
        await message.delete()

    await UserStates.process.set()

    await message.answer(
        text=main_page_format(language),
        reply_markup=menu_keyboard(language)
    )


def register_returnable_handlers(dispatcher: Dispatcher):
    filter = lambda query: query.data == 'back'

    dispatcher.register_message_handler(cmd_start, commands='start', state='*')
    dispatcher.register_callback_query_handler(back_to_main_menu_handler, filter, state='*')
    dispatcher.register_message_handler(
        back_to_main_menu_handler, text=[option['main']['uz'], option['main']['ru']], state='*'
    )
