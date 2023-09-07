from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from src.helpers.utils import language_definer, translator
from src.helpers.keyboard_buttons import user, option


def menu_keyboard(language):
    lang = language_definer(language)

    buttons = [
        [KeyboardButton(user['pages'][lang]['order']), KeyboardButton(user['pages'][lang]['exist'])],
        [KeyboardButton(user['pages'][lang]['my_orders']), KeyboardButton(user['pages'][lang]['basket'])],
        [KeyboardButton(user['pages'][lang]['settings'])]
    ]

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)


def order_keyboard(language):
    lang = language_definer(language)

    buttons = [
        [
            InlineKeyboardButton(user['my_orders'][lang]['active'], callback_data='active_orders'),
            InlineKeyboardButton(user['my_orders'][lang]['received'], callback_data='received_orders'),
        ],
        [InlineKeyboardButton(option['main'][lang], callback_data='back')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def foods_keyboard(foods, language, limit=3):
    buttons, arr = [], []

    lang = language_definer(language)

    for food in foods:
        arr.append(InlineKeyboardButton(text=food['title'], callback_data=f"sfood_{food['id']}"))

        if len(arr) % limit == 0:
            buttons.append(arr)
            arr = []

    buttons.append(arr)

    buttons.append([InlineKeyboardButton(option['main'][lang], callback_data='back')])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def exist_foods_keyboard(foods, language, limit=3):
    buttons, arr = [], []

    lang = language_definer(language)

    for item in foods:
        arr.append(InlineKeyboardButton(text=item['food']['title'], callback_data=f"sef_{item['food']['id']}"))

        if len(arr) % limit == 0:
            buttons.append(arr)
            arr = []

    buttons.append(arr)

    buttons.append([InlineKeyboardButton(option['main'][lang], callback_data='back')])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def single_exist_food_keyboard(exist_food, language, count=1):
    lang = language_definer(language)

    buy, query = translator("Sotib olish", "Покупка", language), f"{exist_food['food']['id']}_{count}"

    buttons = [
        [
            InlineKeyboardButton(text='-', callback_data=f"min_{query}"),
            InlineKeyboardButton(text=f"{count}", callback_data=f"show_{query}"),
            InlineKeyboardButton(text='+', callback_data=f"add_{query}")
        ],
        [InlineKeyboardButton(text=buy, callback_data=f"buy_{query}")],
        [InlineKeyboardButton(option['back'][lang], callback_data='back')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def food_keyboard(food_id, language):
    lang = language_definer(language)

    basket = translator("Savatga qo'shish", "Добавить в корзину", language)

    buttons = [
        [InlineKeyboardButton(text=basket, callback_data=f'tobsk_{food_id}')],
        [InlineKeyboardButton(option['back'][lang], callback_data='back')]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def single_food_keyboard(item, language):
    lang = language_definer(language)

    buttons = [[
        InlineKeyboardButton(text='-', callback_data=f"min_{item['id']}"),
        InlineKeyboardButton(text=f"{item['count']}", callback_data=f"show_{item['id']}"),
        InlineKeyboardButton(text='+', callback_data=f"add_{item['id']}")
    ],
        [InlineKeyboardButton(option['back'][lang], callback_data='back')]
    ]

    # buttons.append()

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def active_orders_keyboard(orders, limit, language):
    buttons, arr = [], []

    lang = language_definer(language)

    for order in orders:
        arr.append(InlineKeyboardButton(text=order['order_id'], callback_data=f"sao_{order['id']}"))

        if len(arr) % limit == 0:
            buttons.append(arr)
            arr = []

    buttons.append(arr)

    buttons.append([InlineKeyboardButton(option['back'][lang], callback_data='back')])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def single_active_order_keyboard(order, language):
    lang = language_definer(language)

    buttons = [
        [InlineKeyboardButton(text="QR CODE", callback_data=f"qrcode_{order['id']}")],
    ]

    if order['status'] != 'ready':
        buttons.append([InlineKeyboardButton(text=option['cancel'][lang], callback_data=f"order_cancel_{order['id']}")])

    buttons.append(
        [InlineKeyboardButton(text=option['back'][lang], callback_data=f'back')],
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def settings_keyboard(language):
    lang = language_definer(language)

    buttons = [
        [KeyboardButton(user['settings'][lang]['phone']), KeyboardButton(user['settings'][lang]['language'])],
        [KeyboardButton(option['main'][lang])]
    ]

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)


def basket_keyboard(order, language):
    lang = language_definer(language)

    buttons = []

    for item in order:
        buttons.append([
            InlineKeyboardButton(text='-', callback_data=f"min_{item['id']}"),
            InlineKeyboardButton(text=f"{item['count']}", callback_data=f"show_{item['id']}"),
            InlineKeyboardButton(text='+', callback_data=f"add_{item['id']}")
        ])

    ordering = translator("Buyurtma berish", "Оформить заказ", language)
    clear = translator("Savatni tozalash", "Очистить корзину", language)

    buttons.append([
        InlineKeyboardButton(text=ordering, callback_data=f"ordering"),
        InlineKeyboardButton(text=clear, callback_data='clear_basket')
    ])

    buttons.append([InlineKeyboardButton(option['main'][lang], callback_data='back')])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
