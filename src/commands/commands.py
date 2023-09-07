from aiogram import Dispatcher
from aiogram.types import BotCommand

commands = [
    BotCommand(command="start", description="Запустить"),
]


async def set_up_commands(dispatcher: Dispatcher) -> None:
    await dispatcher.bot.delete_my_commands()

    await dispatcher.bot.set_my_commands(commands=commands)
