from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from qrcode import QRCode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.constants import ERROR_CORRECT_L

from base64 import b64encode
from bs4 import BeautifulSoup

from io import BytesIO

from src.controllers.billing import BillingController
from src.helpers.keyboard_buttons import option


def qrcode_generator(data):
    qr = QRCode(
        error_correction=ERROR_CORRECT_L,
    )
    qr.add_data(data)
    qr.make()

    qr_image = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())

    # qr_image = make(data)

    qr_image_bytes = BytesIO()
    qr_image.save(qr_image_bytes)
    qr_image_bytes.seek(0)

    return qr_image_bytes


def language_definer(language):
    return 'uz' if language == option['language']['uz'] else 'ru'


def is_num(number) -> bool:
    try:
        int(number)
        return True
    except ValueError:
        return False


def translator(sentence_uz, sentence_ru, language=option['language']['ru']):
    return sentence_uz if language == option['language']['uz'] else sentence_ru


def status_translator(status, language):
    lang = language_definer(language)
    return option['order_status'][lang][status]


def get_count_active_and_delivered_orders(orders):
    active, delivered = 0, 0

    for order in orders:
        if order['status'] not in ['in_stock', 'cancelled']:
            if order['status'] in ['formationed', 'accepted', 'ready']:
                active += 1
            elif order['status'] in ['delivered']:
                delivered += 1

    return dict(active=active, delivered=delivered)


def encode_basic_auth(username, password):
    credentials = f"{username}:{password}"
    return b64encode(credentials.encode('utf-8')).decode('utf-8')


def parse_text_to_html(text):
    return BeautifulSoup(text, 'html.parser').get_text()


def get_access_token(tokens: dict):
    return tokens['access']


def get_chat_ids_from_storage(chat_ids):
    ids = []

    for x, y in chat_ids:
        ids.append(x)

    return ids


class Pagination:
    def __init__(self, data_type: str):
        self.data_type = data_type

    async def paginate(self, page: int, limit: int, token: str, language: str = option['language']['ru']) -> dict:
        text, clause, data, all_data, keyboard, arr, author, status = "", "", [], [], InlineKeyboardMarkup(), [], {}, True

        offset = limit * (page - 1)

        controller = BillingController(token)

        if self.data_type == 'ORDER':
            # todo get received_orders
            data = await controller.get_received_orders(page=page, limit=limit)
            # todo get all_received_orders
            all_data = await controller.get_received_orders(is_pagination=True)
            clause = 'rec_orders'

        if not data:
            if self.data_type == 'ORDER':
                text = translator("Hozircha hech narsa sotib olmagansiz", "Вы еще ничего не купили", language)
                # keyboard = menu_keyboard(language)

            status = False

            return dict(message=text, keyboard=keyboard, status=status)

        text = translator(
            f'<b>Hozirgi: {offset + 1}-{len(data) + offset}, Jami: {len(all_data)}</b>\n\n',
            f'<b>Текущий: {offset + 1}-{len(data) + offset}, Общий: {len(all_data)}</b>\n\n',
            language
        )

        for i, info in enumerate(data, start=1):
            callback_data = ""

            if self.data_type == 'ORDER':
                callback_data = f"sorder_{info['id']}"

            obj = InlineKeyboardButton(text=f'{i}', callback_data=callback_data)

            arr.append(obj)

            if len(arr) % limit == 0:
                keyboard.row(*arr)
                arr = []

            if self.data_type == 'ORDER':
                text += f"<b>{i}.</b>  {info['order_id']} - {info['date']}\n"

        keyboard.row(*arr)

        left_page_callback_data = f'left#{clause}#{page - 1}' if page != 1 else 'none'
        right_page_callback_data = f'right#{clause}#{page + 1}' if len(data) + offset != len(all_data) else 'none'

        inline_keyboard_buttons = [
            InlineKeyboardButton(text='⬅', callback_data=left_page_callback_data),
            InlineKeyboardButton(text='❌', callback_data="delete"),
            InlineKeyboardButton(text='➡', callback_data=right_page_callback_data)
        ]

        keyboard.row(*inline_keyboard_buttons)

        return dict(message=text, keyboard=keyboard, status=status)
