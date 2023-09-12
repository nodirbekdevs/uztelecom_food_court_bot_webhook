from typing import Optional
from aiohttp import ClientSession
from src.helpers.keyboard_buttons import option
from src.helpers.environ import BASE_URL


class AccountController:
    def __init__(self):
        self.url = f'{BASE_URL}/account'
        self.headers = {
            'Accept': 'application/json'
        }

    async def send_verification_code(self, data: dict) -> Optional[dict]:
        async with ClientSession() as session:
            async with session.post(f'{self.url}/send_verification_code/', json=data) as response:
                if response.status != 200:
                    return None

                return await response.json()

    async def check_verification_code(self, data: dict) -> Optional[dict]:
        async with ClientSession(headers=self.headers) as session:
            async with session.post(f'{self.url}/check_verification_code/', json=data) as response:

                if response.status != 200:
                    return None

                return await response.json()

    async def me(self, token) -> Optional[dict]:
        self.headers.update(Authorization=f'Bearer {token}')

        async with ClientSession(headers=self.headers) as session:
            async with session.get(f'{self.url}/me/') as response:

                if response.status != 200:
                    return None

                user = await response.json()
                user['language'] = option['language']['ru']
                return user

    async def token_refresh(self, data: dict):
        async with ClientSession() as session:
            async with session.post(f'{self.url}/token/refresh/', json=data) as response:

                if response.status != 200:
                    return None

                response_json = await response.json()

                return response_json
