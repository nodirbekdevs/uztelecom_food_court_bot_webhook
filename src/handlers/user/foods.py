from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ChatActions
from aiogram.dispatcher import FSMContext

from src.loader import dp
from src.controllers.foods import FoodController
from src.controllers.account import AccountController
from src.controllers.billing import BillingController
from src.helpers.format import foods_format, single_food_format, show_food_format
from src.helpers.utils import translator, is_num, get_access_token
from src.helpers.keyboard_buttons import user, option
from src.keyboards.user import foods_keyboard, single_food_keyboard, food_keyboard
from src.keyboards.option import exception_keyboard
from src.states.food import FoodStates
from src.states.user import UserStates


@dp.message_handler(text=[user['pages']['uz']['order'], user['pages']['ru']['order']], state=UserStates.process)
async def user_foods_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        token = get_access_token(data.get(f'{message.from_user.id}_token'))

    # todo get user request
    user = await AccountController().me(token)

    # todo get all foods handler
    foods = await FoodController().get_foods_for_order()

    await FoodStates.process.set()

    async with state.proxy() as data:
        data[f'{message.from_user.id}_user_language'] = user['language']

    message_text = translator(
        "Oshxonamizda quyidagi taomlar mavjud", "На нашей кухне есть следующие блюда", user['language']
    )

    await message.answer(message_text, reply_markup=ReplyKeyboardRemove())
    await message.answer(
        text=foods_format(foods),
        reply_markup=foods_keyboard(foods, user['language'])
    )


@dp.callback_query_handler(lambda query: query.data.startswith('sfood_'), state=FoodStates.process)
async def single_food_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    # todo get food request
    food = await FoodController().get_one_food(int(query.data.split('_')[1]))

    if not food:
        error_message = translator("Birozdan so'ng qaytarib ko'ring", "Попробуйте позже", language)
        await query.message.answer(error_message)
        return

    message_text = single_food_format(food, language)
    keyboard = food_keyboard(food['id'], language)

    # todo get order handler item
    basket = await BillingController(token).cart()

    if basket:
        for item in basket:
            if item.get('food')['id'] == food['id']:
                keyboard = single_food_keyboard(item, language)

    await FoodStates.single.set()

    await dp.bot.send_chat_action(query.message.chat.id, ChatActions.TYPING)

    if food.get('image'):
        await query.message.delete()
        await query.message.answer_photo(
            photo=food['image'], caption=message_text, reply_markup=keyboard
        )
        return

    await query.message.edit_text(message_text, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data == 'back', state=FoodStates.single)
async def back_from_single_food_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')

    # todo get order foods request
    foods = await FoodController().get_foods_for_order()

    await FoodStates.process.set()

    await query.message.delete()
    await query.message.answer(
        text=foods_format(foods),
        reply_markup=foods_keyboard(foods, language)
    )


@dp.callback_query_handler(lambda query: query.data.startswith('tobsk_'), state=FoodStates.single)
async def request_exception_moment_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        token = get_access_token(data.get(f'{query.from_user.id}_token'))
        language = data.get(f'{query.from_user.id}_user_language')

    food_id = int(query.data.split('_')[1])

    item_data = dict(food=food_id, count=1)

    food = await FoodController().get_one_food(food_id)

    controller = BillingController(token)

    # todo create order item request
    await controller.create_order_item(item_data)

    basket = await controller.cart()

    message_text, keyboard = single_food_format(food, language), []

    order_item = dict()

    if basket:
        for item in basket:
            if item['food']['id'] == food['id']:
                order_item = item
                keyboard = single_food_keyboard(item, language)

    message_text = translator("Mahsulot savatingizga qo'shildi", "Товар добавлен в корзин", language)
    await query.message.answer(message_text)

    await dp.bot.send_chat_action(query.message.chat.id, ChatActions.TYPING)

    if order_item['food']['image']:
        await query.message.delete()
        await query.message.answer_photo(order_item['food']['image'], caption=message_text, reply_markup=keyboard)
        return

    await query.message.edit_text(text=message_text, reply_markup=keyboard)


# @dp.callback_query_handler(lambda query: query.data.startswith('tobsk_'), state=FoodStates.single)
# async def request_exception_moment_handler(query: CallbackQuery, state: FSMContext):
#     async with state.proxy() as data:
#         language = data.get(f'{query.from_user.id}_user_language')
#
#     await query.message.delete()
#
#     await FoodStates.exception.set()
#
#     message_text = translator(
#         f"Istisno holatlar borm ? Malasan: pishloq solmastan solmastan tayyorlash kerak",
#         f"Есть ли исключения ? Маласан: следует готовить без сырной начинки.",
#         language
#     )
#
#     await query.message.answer(message_text, reply_markup=exception_keyboard(language))
#
#     async with state.proxy() as data:
#         data[f'{query.from_user.id}_order_food_id'] = int(query.data.split('_')[1])


# @dp.message_handler(state=FoodStates.exception)
# async def order_item_creation_handler(message: Message, state: FSMContext):
#     async with state.proxy() as data:
#         language = data.get(f'{message.from_user.id}_user_language')
#         food_id = data.get(f'{message.from_user.id}_order_food_id')
#         token = get_access_token(data.get(f'{message.from_user.id}_token'))
#
#     if is_num(message.text):
#         error_text = translator("Raqam jo'natmang!", "Не отправляйте номер!", language)
#         await message.answer(error_text)
#         return
#
#     await FoodStates.single.set()
#
#     food = await FoodController().get_one_food(food_id)
#
#     if message.text in [option['back']['uz'], option['back']['ru']]:
#         message_text = translator(f"Mahsulot - {food['title']}", f"Продукт — {food['title']}", language)
#         await message.answer(message_text, reply_markup=ReplyKeyboardRemove())
#
#         if food.get('image'):
#             await message.answer_photo(
#                 photo=food['image'],
#                 caption=single_food_format(food, language),
#                 reply_markup=food_keyboard(food_id, language)
#             )
#             return
#
#         await message.answer(
#             single_food_format(food, language),
#             reply_markup=food_keyboard(food_id, language)
#         )
#         return
#
#     item_data = dict(food=food_id, count=1, comment=message.text)
#
#     if message.text in [option['exception']['uz'], option['exception']['ru']]:
#         del item_data['comment']
#
#     controller = BillingController(token)
#
#     # todo create order item request
#     await controller.create_order_item(item_data)
#
#     basket = await controller.cart()
#
#     message_text, keyboard = single_food_format(food, language), []
#
#     order_item = dict()
#
#     if basket:
#         for item in basket:
#             if item['food']['id'] == food['id']:
#                 order_item = item
#                 keyboard = single_food_keyboard(item, language)
#
#     message_text = translator("Mahsulot savatingizga qo'shildi", "Товар добавлен в корзин", language)
#     await message.answer(message_text, reply_markup=ReplyKeyboardRemove())
#
#     await dp.bot.send_chat_action(message.chat.id, ChatActions.TYPING)
#
#     if order_item['food']['image']:
#         await message.answer_photo(order_item['food']['image'], caption=message_text, reply_markup=keyboard)
#         return
#
#     await message.answer(text=message_text, reply_markup=keyboard)


@dp.callback_query_handler(
    lambda query: query.data.startswith('add_') or query.data.startswith('min_'), state=FoodStates.single
)
async def control_food_handler(query: CallbackQuery, state: FSMContext):
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

    message_text = single_food_format(order_item['food'], language)

    await dp.bot.send_chat_action(query.message.chat.id, ChatActions.TYPING)

    if item_data['count'] == 0:
        await controller.delete_order_item(order_item_id)

        keyboard = food_keyboard(order_item['food']['id'], language)

        if order_item.get('food').get('image'):
            await query.message.delete()
            await query.message.answer_photo(
                photo=order_item['food']['image'],
                caption=message_text,
                reply_markup=keyboard
            )
            return

        await query.message.edit_text(message_text, keyboard)
        return

    # todo update order item request
    await controller.update_order_item_count(order_item_id, item_data)

    # todo get updated order item
    order_item = await controller.get_order_item(order_item_id)

    keyboard = single_food_keyboard(order_item, language)

    if order_item.get('food').get('image'):
        await query.message.delete()
        await query.message.answer_photo(order_item['food']['image'], caption=message_text, reply_markup=keyboard)
        return

    await query.message.edit_text(text=message_text, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith('show_'), state=FoodStates.single)
async def show_food_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')
        token = get_access_token(data.get(f'{query.from_user.id}_token'))

    item_id = int(query.data.split('_')[1])

    # todo get order item request
    order_item = await BillingController(token).get_order_item(item_id)

    await query.answer(text=show_food_format(order_item, language), show_alert=True)
