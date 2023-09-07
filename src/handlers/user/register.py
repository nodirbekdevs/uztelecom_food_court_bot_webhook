from aiogram.types import Message, ContentTypes
from aiogram.dispatcher import FSMContext
from src.loader import dp
from src.controllers.account import AccountController
from src.helpers.format import main_page_format
from src.helpers.utils import is_num, translator, get_access_token
from src.helpers.keyboard_buttons import option
from src.keyboards.user import menu_keyboard
from src.keyboards.option import send_contact_keyboard, back_keyboard
from src.states.register import RegisterStates
from src.states.user import UserStates
from src.business_logic.register import send_contact


# @dp.message_handler(commands='start')
# async def cmd_start(message: Message, state: FSMContext):
#     # todo get user request
#     user = await AccountController(message.from_user.id).me()
#
#     if user:
#         message_text = main_page_format(user['language'])
#         await message.answer(message_text, reply_markup=menu_keyboard(user['language']))
#         return
#
#     await RegisterStates.language.set()
#     await message.answer(introduction_format(message.from_user.first_name), reply_markup=language_keyboard())


# @dp.message_handler(state=RegisterStates.language)
# async def requesting_phone_handler(message: Message, state: FSMContext):
#     if is_num(message.text) or message.text not in [option['language']['uz'], option['language']['ru']]:
#         await message.answer(
#             "Iltimos keltirilgan tildan birini tanlang\nПожалуйста, выберите один из перечисленных языков"
#         )
#         return
#
#     user_language = message.text
#
#     first_message = translator("Telefon raqamingizni yuboring.", "Отправьте свой номер телефона.", user_language)
#     second_message = translator(
#         f"Contactingizni jo'natish uchun {option['send']['uz']} ni bosing",
#         f"Нажмите {option['send']['ru']} тобы отправить ваш контакт",
#         user_language
#     )
#
#     async with state.proxy() as data:
#         data['user_language'] = user_language
#
#     await RegisterStates.phone.set()
#
#     await message.answer(first_message)
#     await message.answer(second_message, reply_markup=send_contact_keyboard(user_language))


async def cmd_start(message: Message, state: FSMContext):
    token = ''

    async with state.proxy() as data:
        if data.get(f'{message.from_user.id}_token'):
            token = get_access_token(data.get(f'{message.from_user.id}_token'))

        if data.get(f'{message.from_user.id}_user_received_order_page'):
            del data[f'{message.from_user.id}_user_received_order_page']

    # todo get user request
    user = await AccountController().me(token)

    if user:
        await UserStates.process.set()
        await message.answer(text=main_page_format(user['language']), reply_markup=menu_keyboard(user['language']))
        return

    # await send_contact(message)


@dp.message_handler(content_types=ContentTypes.ANY, state=RegisterStates.phone)
async def requesting_verification_code_handler(message: Message, state: FSMContext):
    # if not message.text or not message.contact:
    #     pass

    if message.text:
        if message.text in [option['back']['uz'], option['back']['ru']]:
            await send_contact(message)
            return
        else:
            error_message = translator(
                "Tugma orqali raqamingizni yuboring", "Отправьте свой номер через кнопку",
            )
            await message.answer(error_message)
            return

    phone_number = message.contact.phone_number

    if '+' not in phone_number:
        phone_number = f'+{message.contact.phone_number}'

    sms = await AccountController().send_verification_code(
        dict(phone_number=phone_number)
    )

    if sms is None:
        error_message = translator("Uzur siz botdan foydalana olmaysiz.", "К сожалению, вы не можете использовать бота.")
        await message.answer(error_message, reply_markup=send_contact_keyboard(option['language']['ru']))
        return

    message_text = translator(
        "Telefon raqamingizga kod yuborildi.", "Код был отправлен на ваш номер телефона.", option['language']['ru']
    )

    async with state.proxy() as data:
        data[f'{message.from_user.id}_user_phone'] = phone_number

    await RegisterStates.verification_code.set()

    await message.answer(message_text, reply_markup=back_keyboard(option['language']['ru']))


@dp.message_handler(state=RegisterStates.verification_code)
async def user_creation_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        phone_number = data.get(f'{message.from_user.id}_user_phone')

    if message.text in [option['back']['uz'], option['back']['ru']]:
        await send_contact(message)
        return

    if not is_num(message.text):
        error_text = translator("Telefonningizga raqamlar yuborilgan.", "Номера отправлены на ваш телефон.")

        await message.answer(error_text)
        return

    sms_checking = await AccountController().check_verification_code(
        dict(phone_number=phone_number, security_code=int(message.text))
    )

    if sms_checking is None:
        error_text = translator(
            "Telefonningizga yuborilgan kodni kiriting.", "Введите код, отправленный на ваш телефон."
        )

        await message.answer(error_text)
        return

    await UserStates.process.set()

    async with state.proxy() as data:
        data[f'{message.from_user.id}_token'] = sms_checking['tokens']
        del data[f'{message.from_user.id}_user_phone']

    await message.answer(
        main_page_format(option['language']['ru']), reply_markup=menu_keyboard(option['language']['ru'])
    )
