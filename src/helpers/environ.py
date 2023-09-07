from os import environ
import dotenv

dotenv.load_dotenv()

BOT_TOKEN = environ['BOT_TOKEN']
BASE_URL = environ.get('BASE_URL')
REDIS_HOST = environ.get('REDIS_HOST')
REDIS_PORT = environ.get('REDIS_PORT')
REDIS_DB = environ.get('REDIS_DB')

WEBHOOK_BASE_URL = environ['WEBHOOK_BASE_URL']
WEBHOOK_PATH = f"/bot_webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}"
