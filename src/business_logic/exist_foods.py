from src.helpers.utils import translator
from src.helpers.format import exist_foods_format, single_exist_food_format
from src.keyboards.user import exist_foods_keyboard, single_exist_food_keyboard, menu_keyboard
from src.states.exist_food import ExistFoodStates
from src.states.user import UserStates


async def send_exist_foods(message, exist_foods, language):
    error_text = translator(
        "Uzur bu taomni boshqa odam sotib olib bo'di.", "Извините, эту еду купил кто-то другой.", language
    )

    await ExistFoodStates.process.set()

    await message.answer(error_text)

    await message.answer(
        text=exist_foods_format(exist_foods), reply_markup=exist_foods_keyboard(exist_foods, language)
    )


async def send_exist_food(message, exist_food, language, exist_food_count=0):
    message_text, keyboard = single_exist_food_format(exist_food, language), single_exist_food_keyboard(exist_food, language)

    await ExistFoodStates.single.set()

    if exist_food_count > 0:
        if exist_food['total_count'] < exist_food_count:
            error_text = translator(
                f"Afsus hozirgi vaqtda {exist_food_count} ta bu {exist_food['food']['title']} taom yo'q",
                f"К сожалению, это блюдо {exist_food['food']['title']} в настоящее время недоступно в {exist_food_count}",
                language
            )
            await message.answer(error_text)

    if exist_food.get('food')['image']:
        await message.answer_photo(photo=exist_food['food']['image'], caption=message_text, reply_markup=keyboard)
        return

    await message.answer(text=message_text, reply_markup=keyboard)


async def does_not_exist_food(message, language):
    error_message = translator(
        "Mavjud emas. Buyurtma bering.", "Не осталось в наличии. Разместите заказ.", language
    )

    await UserStates.process.set()
    await message.answer(error_message, reply_markup=menu_keyboard(language))