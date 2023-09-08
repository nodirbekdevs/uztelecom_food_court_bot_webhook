from fastapi import FastAPI
from aiogram.types import Update
from aiogram import Dispatcher, Bot
from logging import INFO, basicConfig, warning

from aiogram.utils.executor import start_polling

from src.loader import dp, scheduler
from src.commands.commands import set_up_commands
from src.helpers.environ import WEBHOOK_URL, WEBHOOK_PATH
from src.handlers.user import register_returnable_handlers, basket, exist_foods, foods, orders, register, settings
from src.schedule.schedule import run_schedule
from src.middlewares.authorization import AuthorizationMiddleware


# async def startup(dispatcher: Dispatcher):
#     register_returnable_handlers(dispatcher)
#
#     dispatcher.setup_middleware(middleware=AuthorizationMiddleware())
#
#     run_schedule()
#     # webhook = await dispatcher.bot.get_webhook_info()
#
#     # if webhook.url != WEBHOOK_URL:
#     #     if not webhook.url:
#     #         await dispatcher.bot.delete_webhook()
#     #
#     #     await dispatcher.bot.set_webhook(
#     #         url=WEBHOOK_URL
#     #     )
#
#     await set_up_commands(dispatcher)
#     basicConfig(level=INFO)
#
#
# async def shutdown(dispatcher: Dispatcher):
#     scheduler.shutdown()
#     await dispatcher.bot.delete_webhook()
#     await dispatcher.bot.session.close()
#     await dp.storage.close()
#     await dp.storage.wait_closed()
#     warning("Shutting down..")
#
#
# if __name__ == '__main__':
#     start_polling(dp, on_startup=startup, on_shutdown=shutdown, skip_updates=True)


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    dp.setup_middleware(middleware=AuthorizationMiddleware())

    register_returnable_handlers(dp)

    run_schedule()

    webhook = await dp.bot.get_webhook_info()

    if webhook.url != WEBHOOK_URL:
        if not webhook.url:
            await dp.bot.delete_webhook()
        await dp.bot.set_webhook(
            url=WEBHOOK_URL
        )

    await set_up_commands(dp)
    basicConfig(level=INFO)


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(dp.bot)
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    scheduler.shutdown()
    # await dp.bot.delete_webhook()
    # await dp.bot.get_session().close()
    # await dp.bot.get_session().wait_closed()
    await dp.storage.close()
    await dp.storage.wait_closed()
    warning("Shutting down..")

if __name__ == "__main__":
    from uvicorn import run

    run("src.app:app", host="0.0.0.0", port=8250, reload=True)
