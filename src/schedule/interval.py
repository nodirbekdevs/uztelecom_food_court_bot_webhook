from src.controllers.account import AccountController
from src.loader import storage
from src.helpers.utils import get_chat_ids_from_storage


async def update_token():
    states_list = await storage.get_states_list()

    datas = get_chat_ids_from_storage(states_list)

    for data in datas:
        state_data = await storage.get_data(chat=data)

        key = f'{data}_token'

        if key in state_data:
            tokens = await AccountController().token_refresh(dict(refresh=state_data[key]['refresh']))

            if tokens:
                new_state_data = state_data.copy()
                new_state_data[key]['access'] = tokens['access']

                await storage.set_data(chat=data, data=new_state_data)
