from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from src.loader import dp
from src.controllers.account import AccountController
from src.helpers.format import user_format
from src.helpers.utils import translator, get_access_token
from src.helpers.keyboard_buttons import user, option
from src.states.user import UserStates


@dp.message_handler(text=[user['pages']['uz']['settings'], user['pages']['ru']['settings']], state=UserStates.process)
async def settings_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:

        token = get_access_token(data.get(f"{message.from_user.id}_token"))

    account = await AccountController().me(token)

    await message.answer(user_format(account))

#
#
# @dp.message_handler(text=[user['pages']['uz']['settings'], user['pages']['ru']['settings']])
# async def user_settings_handler(message: Message, state: FSMContext):
#     # todo get user request
#     user = UserController.get_by_telegram_id(message.from_user.id)
#
#     await SettingStates.process.set()
#
#     async with state.proxy() as data:
#         data['user_language'] = user['language']
#
#     await message.answer(
#         text=user_format(user, user['language']),
#         reply_markup=settings_keyboard(user['language'])
#     )
#
#
# @dp.message_handler(
#     text=[user['settings']['uz']['phone'], user['settings']['ru']['phone']], state=SettingStates.process
# )
# async def requesting_user_phone_number_for_update_handler(message: Message, state: FSMContext):
#     state_data = await state.get_data()
#
#     message_text = translator(
#         "O'zgartirmoqchi bo'lgan raqamingizni kiriting",
#         "Введите номер, которое хотите изменить",
#         state_data['user_language']
#     )
#
#     await SettingStates.phone.set()
#     await message.answer(message_text, reply_markup=back_keyboard(state_data['user_language']))
#
#
# @dp.message_handler(state=SettingStates.phone)
# async def updating_user_number_handler(message: Message, state: FSMContext):
#     # todo get user request
#     user = UserController.get_by_telegram_id(message.from_user.id)
#
#     if message.text in [option['back']['uz'], option['back']['ru']]:
#         error_message = translator("Bekor qilindi", "Отменено", user['language'])
#         await message.answer(error_message)
#         await user_settings_handler(message, state)
#         return
#
#     if not is_num(message.text):
#         error_message = translator("Raqam jo'nating!", "Пришлите номер!", user['language'])
#         await message.answer(error_message)
#         return
#
#     # todo update user phone number request
#     user['phone_number'] = message.text
#
#     await SettingStates.process.set()
#
#     await message.answer(
#         text=user_format(user, user['language']),
#         reply_markup=settings_keyboard(user['language'])
#     )
#
#     message_text = translator("Raqamingiz muvaffaqiyatli o'zgartirildi", "Ваше номер успешно изменено", user['language'])
#
#     await message.answer(message_text)
#
#
# @dp.message_handler(
#     text=[user['settings']['uz']['language'], user['settings']['ru']['language']], state=SettingStates.process
# )
# async def requesting_user_language_for_update_handler(message: Message, state: FSMContext):
#     state_data = await state.get_data()
#
#     message_text = translator("Qaysi tilni tanlaysiz", "Какой язык вы выбираете", state_data['user_language'])
#
#     await SettingStates.language.set()
#     await message.answer(message_text, reply_markup=language_keyboard(language=state_data['user_language'], is_editing=True))
#
#
# @dp.message_handler(state=SettingStates.language)
# async def updating_user_lang_handler(message: Message, state: FSMContext):
#     # todo get user request
#     user = UserController.get_by_telegram_id(message.from_user.id)
#
#     if message.text in [option['back']['uz'], option['back']['ru']]:
#         error_message = translator("Bekor qilindi", "Отменено", user['language'])
#         await message.answer(error_message)
#         await user_settings_handler(message, state)
#         return
#
#     if is_num(message.text):
#         error_message = translator("Raqam jo'nating!", "Пришлите номер!", user['language'])
#         await message.answer(error_message)
#         return
#
#     if message.text not in [option['language']['uz'], option['language']['ru']]:
#         error_message = translator(
#             "O'zingizga mos keladigan tugmani bosib tilni tanlang",
#             "Выберите язык, который вам подходит, нажав на кнопку",
#              user.lang
#         )
#         await message.answer(error_message)
#         return
#
#     # todo update user language request
#     user['language'] = message.text
#
#     await SettingStates.process.set()
#
#     await message.answer(
#         text=user_format(user, user['language']),
#         reply_markup=settings_keyboard(user['language'])
#     )
#
#     message_text = translator(
#         "Platformadagi tilingiz muvaffaqiyatli o'zgartirildi", "Язык вашей платформы успешно изменен", user['language']
#     )
#
#     await message.answer(message_text)
