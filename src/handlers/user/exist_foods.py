from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ChatActions
from aiogram.dispatcher import FSMContext

from src.loader import dp
from src.business_logic.exist_foods import send_exist_food, send_exist_foods, does_not_exist_food
from src.controllers.account import AccountController
from src.controllers.billing import BillingController
from src.controllers.foods import FoodController
from src.helpers.format import exist_foods_format, single_exist_food_format
from src.helpers.utils import translator, get_access_token, is_num
from src.helpers.keyboard_buttons import user, option
from src.keyboards.user import exist_foods_keyboard, single_exist_food_keyboard
from src.keyboards.option import exception_keyboard
from src.states.exist_food import ExistFoodStates
from src.states.user import UserStates


@dp.message_handler(text=[user['pages']['uz']['exist'], user['pages']['ru']['exist']], state=UserStates.process)
async def user_foods_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        token = get_access_token(data.get(f'{message.from_user.id}_token'))

    # todo get user request
    user = await AccountController().me(token)

    # todo get all foods handler
    foods = await FoodController().in_stock()

    if not foods:
        error_message = translator(
            "Sotuvda mavjud taomlar yo'q. Buyurtma bering.", "В продаже нет блюд. Разместите заказ.", user['language']
        )
        await message.answer(error_message)
        return

    await ExistFoodStates.process.set()

    async with state.proxy() as data:
        data[f'{message.from_user.id}_user_language'] = user['language']

    message_text = translator(
        "Oshxonamizda quyidagi taomlar sotuvda mavjud", "На нашей кухне доступны следующие блюда", user['language']
    )

    await message.answer(message_text, reply_markup=ReplyKeyboardRemove())
    await message.answer(
        text=exist_foods_format(foods),
        reply_markup=exist_foods_keyboard(foods, user['language'])
    )


@dp.callback_query_handler(lambda query: query.data.startswith('sef_'), state=ExistFoodStates.process)
async def single_food_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')

    # todo get food request
    food = await FoodController().get_one_from_stock(int(query.data.split('_')[1]))

    if not food:
        error_message = translator("Birozdan so'ng urinib ko'ring", "Попробуйте позже", language)
        await query.message.answer(error_message)
        return

    message_text, keyboard = single_exist_food_format(food, language), single_exist_food_keyboard(food, language)

    await ExistFoodStates.single.set()

    await dp.bot.send_chat_action(query.message.chat.id, ChatActions.TYPING)

    if food.get('food')['image']:
        await query.message.delete()
        await query.message.answer_photo(
            photo=food['food']['image'], caption=message_text, reply_markup=keyboard
        )
        return

    await query.message.edit_text(message_text, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data == 'back', state=ExistFoodStates.single)
async def back_from_single_food_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')

    # todo get order foods request
    foods = await FoodController().in_stock()

    await ExistFoodStates.process.set()

    await query.message.delete()
    await query.message.answer(
        text=exist_foods_format(foods),
        reply_markup=exist_foods_keyboard(foods, language)
    )


@dp.callback_query_handler(
    lambda query: query.data.startswith('add_') or query.data.startswith('min_'), state=ExistFoodStates.single
)
async def control_food_handler(query: CallbackQuery, state: FSMContext):
    control = query.data.split('_')

    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')

    food_id, exist_food_count = int(control[1]), int(control[2])

    # todo get exist food request
    exist_food = await FoodController().get_one_from_stock(food_id)

    if control[0] == 'add':
        exist_food_count += 1

        if exist_food_count > exist_food['total_count']:
            error_message = translator(
                f"Hozirda bu {exist_food['food']['title']} taomdan sotuvda {exist_food['total_count']} mavjud",
                f"На это блюдо {exist_food['food']['title']} сейчас продается {exist_food['total_count']}",
                language
            )
            await query.answer(text=error_message, show_alert=True)
            return
    elif control[0] == 'min':
        exist_food_count -= 1

        if exist_food_count == 0:
            await query.answer()
            return

    message_text = single_exist_food_format(exist_food, language)
    keyboard = single_exist_food_keyboard(exist_food, language, exist_food_count)

    await dp.bot.send_chat_action(query.message.chat.id, ChatActions.TYPING)

    if exist_food.get('food').get('image'):
        await query.message.delete()
        await query.message.answer_photo(exist_food['food']['image'], caption=message_text, reply_markup=keyboard)
        return

    await query.message.edit_text(text=message_text, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith('show_'), state=ExistFoodStates.single)
async def show_food_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')

    control = query.data.split('_')

    food_id, exist_food_count = int(control[1]), int(control[2])

    # todo get exist food request
    exist_food = await FoodController().get_one_from_stock(food_id)

    message_text = translator(
        f"Siz {exist_food['food']['title']} dan {exist_food_count} ta sotib olmoqchisiz",
        f"Вы хотите купить {exist_food_count} от {exist_food['food']['title']}",
        language
    )

    await query.answer(text=message_text, show_alert=True)


@dp.callback_query_handler(lambda query: query.data.startswith('buy_'), state=ExistFoodStates.single)
async def show_food_handler(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{query.from_user.id}_user_language')

    control = query.data.split('_')

    exist_food_id, exist_food_count = int(control[1]), int(control[2])

    async with state.proxy() as data:
        data[f"{query.from_user.id}_exist_food_id_for_order"] = exist_food_id
        data[f"{query.from_user.id}_exist_food_count_for_order"] = exist_food_count
        data[f"{query.from_user.id}_delete_message"] = query.message.message_id

    message_text = translator(
        f"Istisno holatlar bormi. Malasan:  pishloq solmastan solmastan qilish kerak",
        f"Есть ли исключения. Например: нужно делать без сырной начинки",
        language
    )

    await ExistFoodStates.buy.set()
    await query.message.delete()
    await query.message.answer(message_text, reply_markup=exception_keyboard(language))


@dp.message_handler(state=ExistFoodStates.buy)
async def order_item_creation_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        language = data.get(f'{message.from_user.id}_user_language')
        exist_food_id = data.get(f"{message.from_user.id}_exist_food_id_for_order")
        exist_food_count = data.get(f"{message.from_user.id}_exist_food_count_for_order")
        token = get_access_token(data.get(f'{message.from_user.id}_token'))

    if is_num(message.text):
        error_text = translator("Raqam jo'natmang!", "Не отправляйте номер!", language)
        await message.answer(error_text)
        return

    # await dp.bot.delete_message(chat_id=message.chat.id, message_id=message_id)

    # todo get one exist food request
    exist_food = await FoodController().get_one_from_stock(exist_food_id)

    # todo get foods in stock request
    exist_foods = await FoodController().in_stock()

    if message.text in [option['back']['uz'], option['back']['ru']]:
        if not exist_food:
            await send_exist_foods(message, exist_foods, language)

        await send_exist_food(message, exist_food, language)

    item_data = dict(payment_type='salary', food=exist_food_id, count=exist_food_count, comment=message.text)

    if message.text in [option['exception']['uz'], option['exception']['ru']]:
        del item_data['comment']

    # todo order exist food request
    ordering = await BillingController(token).create_order_food_in_stock(item_data)

    # todo get one exist food request
    exist_food = await FoodController().get_one_from_stock(exist_food_id)

    # todo get foods in stock request
    exist_foods = await FoodController().in_stock()

    if ordering is None:
        if not exist_food and not exist_foods:
            await does_not_exist_food(message, language)
        if not exist_food and exist_foods:
            await send_exist_foods(message, exist_foods, language)
        elif exist_food:
            await send_exist_food(message, exist_food, language, exist_food_count)

    message_text = translator("Buyurtmangiz qabul qilindi", "Ваш заказ принят", language)

    await message.answer(message_text, reply_markup=ReplyKeyboardRemove())

    await ExistFoodStates.process.set()

    if not exist_foods:
        await does_not_exist_food(message, language)

    async with state.proxy() as data:
        del data[f"{message.from_user.id}_exist_food_id_for_order"]
        del data[f"{message.from_user.id}_exist_food_count_for_order"]

    await message.answer(
        text=exist_foods_format(exist_foods), reply_markup=exist_foods_keyboard(exist_foods, language)
    )
