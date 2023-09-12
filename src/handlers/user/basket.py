from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from datetime import datetime, timedelta

from src.loader import dp
from src.controllers.account import AccountController
from src.controllers.billing import BillingController
from src.helpers.format import basket_format, show_food_format
from src.helpers.utils import translator, get_access_token
from src.helpers.keyboard_buttons import user
from src.keyboards.user import menu_keyboard, basket_keyboard
from src.states.basket import BasketStates
from src.states.user import UserStates


@dp.message_handler(text=[user['pages']['uz']['basket'], user['pages']['ru']['basket']], state=UserStates)
async def basket_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        token = get_access_token(data.get(f'{message.from_user.id}_token'))

    # todo get user request
    user = await AccountController().me(token)

    # todo get order request
    basket = await BillingController(token).cart()

    if not basket:
        error_text = translator("Sizning savatingiz bo'sh", "Ваша корзина пуста", user['language'])
        await message.answer(error_text)
        return

    await BasketStates.process.set()

    async with state.proxy() as data:
        data[f'{message.from_user.id}_user_language'] = user['language']

    message_text = translator(
        "Siz buyurtma bermohchi bo'lgan mahsulotlar", "Товары, которые вы хотите заказать", user['language']
    )

    await message.answer(message_text, reply_markup=ReplyKeyboardRemove())
    await message.answer(
        basket_format(basket, user['language']), reply_markup=basket_keyboard(basket, user['language'])
    )


@dp.callback_query_handler(
    lambda query: query.data.startswith('add_') or query.data.startswith('min_'), state=BasketStates.process
)
async def control_basket_handler(query: CallbackQuery, state: FSMContext):
    control = query.data.split('_')

    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    order_item_id = int(control[1])

    controller = BillingController(token)

    # todo get order item request
    order_item = await controller.get_order_item(order_item_id)

    item_data = dict()

    if control[0] == 'add':
        item_data.update(count=order_item['count'] + 1)
    elif control[0] == 'min':
        item_data.update(count=order_item['count'] - 1)

    # todo order item update request
    if item_data['count'] == 0:
        await controller.delete_order_item(order_item_id)
    elif item_data['count'] > 0:
        await controller.update_order_item_count(order_item_id, item_data)

    basket = await controller.cart()

    if not basket:
        await UserStates.process.set()
        await query.message.delete()
        error_text = translator("Savatingiz bo'shatildi", "Ваша корзина опустошена", language)
        await query.message.answer(error_text, reply_markup=menu_keyboard(language))
        return

    await query.message.edit_text(
        text=basket_format(basket, language),
        reply_markup=basket_keyboard(basket, language)
    )


@dp.callback_query_handler(lambda query: query.data.startswith('show_'), state=BasketStates.process)
async def show_basket_item_food_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    item_id = int(query.data.split('_')[1])

    # todo get order item request
    order_item = await BillingController(token).get_order_item(item_id)

    await query.answer(text=show_food_format(order_item, language), show_alert=True)


@dp.callback_query_handler(lambda query: query.data == 'clear_basket', state=BasketStates.process)
async def clear_basket_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    controller = BillingController(token)

    # todo clear order request
    items = await controller.cart()

    for item in items:
        await controller.delete_order_item(item['id'])

    message_text = translator("Savatingiz bo'shatildi", "Ваша корзина опустошена", language)

    await UserStates.process.set()

    await query.message.delete()
    await query.message.answer(message_text, reply_markup=menu_keyboard(language))


@dp.callback_query_handler(lambda query: query.data == 'ordering', state=BasketStates.process)
async def formation_order_handler(query: CallbackQuery, state: FSMContext):
    current_date = datetime.today()

    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    if current_date.weekday()+1 == 6:
        error_text = translator(
            "Siz shanba kuniga buyurtma bera olmaysiz, Ertaga buyurtma bersangiz dushanba kuni uchun buyurtmangizni ola olasiz.",
            "Вы не можете сделать заказ на субботу, если сделаете заказ завтра, то сможете получить заказ на понедельник.",
            language
        )
        await query.answer(text=error_text, show_alert=True)
        return

    order_date = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")

    order_data = dict(date=order_date, payment_type='salary')

    formation = await BillingController(token).order_formation(order_data)

    if not formation:
        error_text = translator("Birozdan so'ng urinib ko'ring", "Попробуйте позже", language)
        await query.answer(text=error_text, show_alert=True)
        return

    await UserStates.process.set()
    await query.message.delete()

    message_text = translator("Buyurtmangiz qabul qilindi.", "Ваш заказ принят.", language)

    await query.message.answer(text=message_text, reply_markup=menu_keyboard(language))

# @dp.callback_query_handler(lambda query: query.data.startswith('ordering_'), state=BasketStates.process)
# async def request_time_handler(query: CallbackQuery, state: FSMContext):
#     state_data = await state.get_data()
#
#     time = is_last_day_of_month()
#
#     keyboard = calendar(time['year'], time['month'], time['current_date'])
#
#     if time.get('date'):
#         keyboard = calendar(time['year'], time['month'], time['current_date'], time['date'])
#
#     message_text = translator(
#         "Qaysi kunga buyurtma bermoqchisiz", "В какой день вы хотите заказать?", state_data['user_language']
#     )
#
#     await BasketStates.date.set()
#
#     await query.message.edit_text(message_text, reply_markup=keyboard)
#
#
# @dp.callback_query_handler(state=BasketStates.date)
# async def order_creation_keyboard(query: CallbackQuery, state: FSMContext):
#     state_data = await state.get_data()
#
#     data = query.data.split('_')
#
#     order_data = dict(payment_type='salary')
#
#     if data[0] == 'info':
#         await query.answer(data[1], show_alert=True)
#         return
#
#     order_data.update(date=data[1])
#
#     # todo order creation request
#     await BillingController(query.from_user.id).order_formation(order_data)
#
#     message_text = translator("Buyurtmangiz qabul qilindi", "Ваш заказ принят", state_data['user_language'])
#
#     await state.finish()
#     await query.message.delete()
#     await query.message.answer(message_text, reply_markup=menu_keyboard(user['language']))


# @dp.callback_query_handler(state=BasketStates.date)
# async def request_payment_handler(query: CallbackQuery, state: FSMContext):
#     # todo get user request
#     user = await UserController.get_by_telegram_id(query.from_user.id)
#
#     print(query.data)
#
#     message_text = translator(
#         "Qaysi usul bilan pul to'lamoqchisiz", "Каким способом вы хотите оплатить?", user['language']
#     )
#
#     await BasketStates.payment.set()
#
#     await query.message.edit_text(message_text, reply_markup=payment_type_keyboard(user['language']))
#
#
# @dp.message_handler(state=BasketStates.payment)
# async def request_payment_handler(message: Message, state: FSMContext):
#     # todo get user request
#     user = await UserController.get_by_telegram_id(message.from_user.id)
#
#     message_text, keyboard = '', []
#
#     if message.text in [option['payment']['uz']['salary'], option['payment']['ru']['salary']]:
#         message_text = translator(
#             "Bu buyurtma pulini oylik maoshingizdan olib qolinishiga rozimisiz? maoshingizdan",
#             "Согласны ли вы, чтобы деньги по этому заказу вычитались из вашей месячной зарплаты? из вашей зарплаты",
#             user['language']
#         )
#         keyboard = confirmation_keyboard(user['language'])
#     elif message.text in [option['payment']['uz']['payment_system'], option['payment']['ru']['payment_system']]:
#         message_text = translator(
#             "Qaysi dastur orqali to'lamoqchisiz", "Через какую программу вы хотите оплатить?", user['language']
#         )
#         keyboard = payment_system_keyboard(user['language'])
#
#     await message.answer(message_text, reply_markup=keyboard)
