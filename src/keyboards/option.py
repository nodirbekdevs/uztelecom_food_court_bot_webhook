from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


from src.helpers.keyboard_buttons import option
from src.helpers.utils import language_definer


def language_keyboard(language=None, is_editing=None):
    lang = language_definer(language)

    buttons = [[KeyboardButton(option['language']['uz']), KeyboardButton(option['language']['ru'])]]

    if is_editing:
        buttons.append([option['back'][lang]])

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)


def back_keyboard(language):
    lang = language_definer(language)

    buttons = [[KeyboardButton(option['back'][lang])]]

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)


def inline_back_keyboard(language):
    lang = language_definer(language)

    buttons = [[InlineKeyboardButton(option['back'][lang], callback_data='back')]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def send_contact_keyboard(language):
    lang = language_definer(language)

    buttons = [[KeyboardButton(option['send'][lang], request_contact=True)]]

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)


def payment_type_keyboard(language):
    lang = language_definer(language)

    buttons = [
        [KeyboardButton(option['payment'][lang]['salary'])],
        [KeyboardButton(option['payment'][lang]['payment_system'])]
    ]

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)


def confirmation_keyboard(language):
    lang = language_definer(language)

    buttons = [[KeyboardButton(option['confirmation'][lang]), KeyboardButton(option['not_to_confirmation'][lang])]]

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)


def payment_system_keyboard(language):
    lang = language_definer(language)

    buttons = [
        [KeyboardButton(option['payment_system']['click']), KeyboardButton(option['payment_system']['payme'])],
        [KeyboardButton(option['back'][lang])]
    ]

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)


def exception_keyboard(language):
    lang = language_definer(language)

    buttons = [
        [KeyboardButton(option['exception'][lang])],
        [KeyboardButton(option['back'][lang])]
    ]

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
