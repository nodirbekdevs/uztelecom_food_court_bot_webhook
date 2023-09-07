from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.helpers.environ import BOT_TOKEN, REDIS_HOST, REDIS_PORT, REDIS_DB

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
storage = RedisStorage2(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
dp = Dispatcher(bot=bot, storage=storage)
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
