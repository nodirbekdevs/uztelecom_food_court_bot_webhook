from aiogram.types import Message, CallbackQuery, InputFile, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from src.loader import dp
from src.controllers.account import AccountController
from src.controllers.billing import BillingController
from src.helpers.format import my_orders_format, active_orders_format, order_format, main_page_format
from src.helpers.utils import (
    translator, qrcode_generator, get_count_active_and_delivered_orders, get_access_token, Pagination
)
from src.helpers.keyboard_buttons import user
from src.keyboards.user import order_keyboard, active_orders_keyboard, single_active_order_keyboard, menu_keyboard
from src.keyboards.option import inline_back_keyboard
from src.states.order import OrderStates
from src.states.user import UserStates


@dp.message_handler(text=[user['pages']['uz']['my_orders'], user['pages']['ru']['my_orders']], state=UserStates.process)
async def user_orders_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        token = get_access_token(data.get(f'{message.chat.id}_token'))

    # todo get user request
    user = await AccountController().me(token)

    # todo get active and received number of orders request
    orders = await BillingController(token).orders()

    counts = get_count_active_and_delivered_orders(orders)

    await OrderStates.process.set()

    async with state.proxy() as data:
        data[f'{message.from_user.id}_user_language'] = user['language']

    message_text = translator("Buyurtmalaringiz", "Ваши заказы", user['language'])

    await message.answer(message_text, reply_markup=ReplyKeyboardRemove())
    await message.answer(
        text=my_orders_format(user['language'], counts['active'], counts['delivered']),
        reply_markup=order_keyboard(user['language'])
    )


@dp.callback_query_handler(lambda query: query.data == 'active_orders', state=OrderStates.process)
async def active_orders_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    # todo get active orders
    orders = await BillingController(token).orders(is_active=True)

    if not orders:
        error_message = translator("Hali buyurtma bermagansiz", "Вы еще не сделали заказ", language)
        await query.answer(error_message, show_alert=True)
        # await query.message.answer(error_message)
        return

    await OrderStates.active_orders.set()

    await query.message.edit_text(
        text=active_orders_format(orders, language),
        reply_markup=active_orders_keyboard(orders, 2, language)
    )


@dp.callback_query_handler(lambda query: query.data == 'back', state=OrderStates.active_orders)
async def back_to_user_orders_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    # todo get orders count
    orders = await BillingController(token).orders()

    counts = get_count_active_and_delivered_orders(orders)

    await OrderStates.process.set()

    await query.message.edit_text(
        text=my_orders_format(language, counts['active'], counts['delivered']),
        reply_markup=order_keyboard(language)
    )


@dp.callback_query_handler(lambda query: query.data.startswith('sao_'), state=OrderStates.active_orders)
async def single_active_order_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    # todo get order request
    order = await BillingController(token).get_order(order_id=int(query.data.split('_')[1]), is_active=True)

    await OrderStates.single_active_order.set()

    await query.message.edit_text(
        text=order_format(order, language),
        reply_markup=single_active_order_keyboard(order, language)
    )


@dp.callback_query_handler(lambda query: query.data == 'back', state=OrderStates.single_active_order)
async def back_from_single_active_order_handler(query: CallbackQuery, state: FSMContext):
    await active_orders_handler(query, state)


@dp.callback_query_handler(lambda query: query.data.startswith(f'qrcode_'), state=OrderStates.single_active_order)
async def send_qrcode_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()

    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    order_id = int(query.data.split('_')[1])

    # todo get order request
    order = await BillingController(token).get_order(order_id=order_id, is_active=True)

    qrcode = qrcode_generator(order['id'])

    # await query.answer(text=qrcode, show_alert=True)

    message_text = translator(
        f"<b>Buyurtmani olish uchun QR.</b> \nBuyurtma raqamingiz: <b>{order['id']}</b>",
        f"<b>QR для получение заказа.</b> \nНомер вашего заказа: <b>{order['id']}</b>",
        language
    )

    await query.message.answer_photo(
        InputFile(qrcode, filename=f"qrcode_{order['order_id']}_{order_id}.png"), caption=message_text
    )


@dp.callback_query_handler(lambda query: query.data.startswith(f'order_cancel_'), state=OrderStates.single_active_order)
async def send_qrcode_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()

    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    order_id = int(query.data.split('_')[2])

    # todo cancel order request
    await BillingController(token).cancel_order(order_id=order_id)

    message_text = translator("Buyurtmangiz bekor qilindi", "Ваш заказ был отменен", language)

    orders = await BillingController(token).orders(is_active=True)

    await query.message.delete()
    await query.message.answer(message_text)

    if not orders:
        await UserStates.process.set()
        await query.message.answer(main_page_format(language), reply_markup=menu_keyboard(language))
        return

    await OrderStates.active_orders.set()

    await query.message.answer(
        text=active_orders_format(orders, language),
        reply_markup=active_orders_keyboard(orders, 2, language)
    )


@dp.callback_query_handler(lambda query: query.data == 'received_orders', state=OrderStates.process)
async def received_orders_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    paginated = await Pagination('ORDER').paginate(1, 6, token, language)

    if not paginated['status']:
        await query.answer(paginated['message'], show_alert=True)
        return

    await OrderStates.delivered_orders.set()

    await query.message.delete()

    # todo check edit text
    await query.message.answer(paginated['message'], reply_markup=paginated['keyboard'])


@dp.callback_query_handler(lambda query: query.data == "delete", state=OrderStates.delivered_orders)
async def back_from_all_received_foods_handler(query: CallbackQuery, state: FSMContext):
    await query.message.delete()

    async with state.proxy() as data:
        if data.get(f'{query.from_user.id}_user_received_order_page'):
            del data[f'{query.from_user.id}_user_received_order_page']

    await user_orders_handler(query.message, state)


@dp.callback_query_handler(
    lambda query: query.data.startswith("left#rec_orders#") or query.data.startswith("right#rec_orders#"),
    state=OrderStates.delivered_orders
)
async def pagination_instructor_tests_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    page = int(query.data.split('#')[2])

    paginated = await Pagination(data_type="ORDER").paginate(
        page, 6, token, language
    )

    async with state.proxy() as data:
        data[f'{query.from_user.id}_user_received_order_page'] = page

    await query.message.edit_text(text=paginated['message'], reply_markup=paginated['keyboard'])


@dp.callback_query_handler(lambda query: query.data == 'none', state=OrderStates.delivered_orders)
async def paginate_received_orders_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')

    message_text = translator(
        "Bu yerda ma'lumotlar yo'q. Siz noto'g'ri betni tanladingiz.",
        "Здесь нет информации. Вы выбрали не ту страницу.",
        language
    )

    await query.answer(text=message_text, show_alert=True)


@dp.callback_query_handler(lambda query: query.data.startswith("sorder_"), state=OrderStates.delivered_orders)
async def get_received_order_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    order_id = int(query.data.split("_")[1])

    # todo get order handler
    order = await BillingController(token).get_order(order_id)

    await OrderStates.single_delivered_order.set()

    await query.message.edit_text(
        text=order_format(order, language),
        reply_markup=inline_back_keyboard(language)
    )


@dp.callback_query_handler(lambda query: query.data == "back", state=OrderStates.single_delivered_order)
async def back_from_get_received_order_handler(query: CallbackQuery, state: FSMContext):
    page = 1

    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

        if data.get(f'{query.from_user.id}_user_received_order_page'):
            page = data[f'{query.from_user.id}_user_received_order_page']

    paginated = await Pagination(data_type="ORDER").paginate(
        page, 6, token, language
    )

    await OrderStates.delivered_orders.set()

    await query.message.edit_text(text=paginated['message'], reply_markup=paginated['keyboard'])
