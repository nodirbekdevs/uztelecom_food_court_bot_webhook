from aiogram.types import Message

from src.helpers.utils import translator
from src.helpers.keyboard_buttons import option
from src.keyboards.option import send_contact_keyboard
from src.states.register import RegisterStates


async def send_contact(message: Message, section_type='REGISTER'):
    second_message = '', ''

    await RegisterStates.phone.set()

    if section_type == 'REGISTER':
        first_message = translator("Telefon raqamingizni yuboring.", "Отправьте свой номер телефона.")
        second_message = translator(
            f"Contactingizni jo'natish uchun {option['send']['uz']} ni bosing",
            f"Нажмите {option['send']['ru']} тобы отправить ваш контакт",
        )
        await message.answer(first_message)
    else:
        second_message = translator(
            "Sizni taniy olmayabman. Iltimos foydalanish uchun ruxsat oling",
            "Я не узнаю вас. Пожалуйста, получите разрешение на использование"
        )

    await message.answer(second_message, reply_markup=send_contact_keyboard(option['language']['ru']))
