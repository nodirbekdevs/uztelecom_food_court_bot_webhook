from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from src.loader import storage
from src.controllers.account import AccountController
from src.business_logic.register import send_contact
from src.helpers.utils import get_access_token
from src.states.register import RegisterStates


class AuthorizationMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    @classmethod
    async def handle_update(cls, sender):
        user_id, chat_id = sender.chat.id, sender.from_user.id

        state = await storage.get_state(chat=chat_id, user=user_id)

        if state in [RegisterStates.phone.state, RegisterStates.verification_code.state]:
            return

        state_data = await storage.get_data(chat=user_id)

        token, key = "", f"{user_id}_token"

        if state_data.get(key):
            token = get_access_token(state_data.get(key))

        auth = await AccountController().me(token)

        if auth is None:
            await sender.delete()

            await send_contact(sender)
            raise CancelHandler()

        return

    async def on_process_message(self, message: Message, data, *args):
        await self.handle_update(message)

    async def on_pre_process_callback_query(self, query: CallbackQuery, data, *args):
        await self.handle_update(query.message)
