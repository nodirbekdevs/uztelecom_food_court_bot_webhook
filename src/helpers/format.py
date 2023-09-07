from src.helpers.keyboard_buttons import option
from src.helpers.utils import translator, parse_text_to_html, status_translator


def introduction_format(name):
    message = (
        f"Bo'timizga xush kelibsiz {name}. <b>Tilni tanlang</b> {option['language']['uz']} \n"
        f"Добро пожаловать {name}. <b>Выберите язык</b> {option['language']['ru']}"
    )

    return message


def main_page_format(language=option['language']['ru']):
    return translator("Bosh sahifa", 'Главная страница', language)


def my_orders_format(language, active, received):
    return translator(
        (
            "Mening buyurtmalarim sahifasi\n"
            f"Faol buyurtmalar {active}\n"
            f"Buyurtmalar tarixi {received}"
        ),
        (
            "Страница моих заказов\n"
            f"Активные заказы {active}\n"
            f"История заказов {received}"
        ),
        language
    )


def user_format(data, is_editing=False):
    message = translator(
        (
            "Ma'lumotlaringiz: \n"
            f"Telefon raqam - {data['phone_number']}.\n"
            f"Tashkilot - {data['organization']}\n"
            f"Tanlangan til - {data['language']}.\n"
        ),
        (
            f"Ваша информация: \n"
            f"Номер телефона - {data['phone_number']}.\n"
            f"Организация - {data['organization']}\n"
            f"Выбранный язык - {data['language']}.\n"
        ),
        data['language']
    )

    if is_editing:
        message += translator((f"\n\nNimani o'zgartirmoqchisiz ?"), (f"\n\nЧто вы хотите изменить ?"), language)

    return message


def foods_format(foods):
    message = ""

    for index, food in enumerate(foods, start=1):
        message += f"<b>{index}.</b> {food['title']} - {food['price']}\n"

    return message


def show_food_format(item, language):
    return translator(
        f"Sizning savatingizda {item['food']['title']} dan {item['count']} ta mavjud",
        f"В вашей корзине есть {item['count']} из {item['food']['title']}",
        language
    )


def single_food_format(food, language):
    description = parse_text_to_html(food['description'])

    return (
        f"<b>{food['title']} - {food['price']}</b>\n"
        f"{description}"
    )


def exist_foods_format(foods):
    message = ""

    for index, item in enumerate(foods, start=1):
        message += f"<b>{index}.</b> {item['food']['title']} - {item['food']['price']} - {item['total_count']}\n"

    return message


def single_exist_food_format(item, language):
    return (
        f"<b>{item['food']['title']} - {item['food']['price']}</b>\n"
        f"{item['food']['description']}\n"
        f"В наличии - {item['total_count']}\n"
        f"Дата - {item['date']}"
    )


def active_orders_format(orders, language):
    message = translator("Buyurtmalaringiz: \n\n", 'Ваши заказы: \n\n', language)

    for order in orders:
        message += f"{order['order_id']} - {order['date']} - {status_translator(order['status'], language)}\n"

    return message


def order_format(order, language):
    message, status, total_sum = "", status_translator(order['status'], language), 0

    message += translator("Buyurtmangiz: \n\n", "Ваш заказ:\n\n", language)

    for item in order['items']:
        total_sum += item['amount']
        message += f"{item['food']['title']} - {item['count']} - {item['amount']}\n"
        message += translator(f"Istisno: ", f"Исключения: ", language)
        message += f"{item['comment']}\n\n" if item['comment'] != '' else '➖\n\n'

    message += translator(f"\nVaqti: {order['date']}\n", f"\nВремя: {order['date']}\n", language)
    message += translator(f"To'lov turi: {order['payment_type']}\n", f"Способ оплаты: {order['payment_type']}\n", language)
    message += translator(f"Umumiy to'lov - {total_sum}\n", f"Общий платеж - {total_sum}\n", language)
    message += translator(f"Holati: {status}", f"Статус: {status}", language)

    return message


def basket_format(order, language):
    message, total_sum = "", 0

    message += translator("Buyurtmangiz: \n\n", "Ваш заказ:\n\n", language)

    for index, item in enumerate(order, start=1):
        total_sum += item['amount']
        message += f"<b>{index}.</b> {item['food']['title']} * {item['count']} - {item['amount']}\n"
        message += translator(f"Istisno: ", f"Исключения: ", language)
        message += f"{item['comment']}\n\n" if item['comment'] != '' else '➖\n\n'

    message += translator(f"Umumiy to'lov - {total_sum}\n", f"Общий платеж - {total_sum}\n", language)

    return message
