from aiohttp import ClientSession
from typing import Optional
from src.helpers.environ import BASE_URL


class BillingController:
    def __init__(self, token):
        self.url = f'{BASE_URL}/billing'
        self.headers = self.headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

    async def cart(self) -> Optional[dict]:
        async with ClientSession(headers=self.headers) as session:
            async with session.get(f'{self.url}/cart/') as response:
                response_json = await response.json()

                if len(response_json) == 0:
                    return None

                return response_json

    async def orders(self, is_active=None, page=None, page_size=None):
        params = dict()

        if is_active:
            params.update(is_active=f'{is_active}')
        if page:
            params.update(page=page)
        if page_size:
            params.update(page_size=page_size)

        async with ClientSession(headers=self.headers) as session:
            async with session.get(url=f'{self.url}/order/', params=params) as response:
                response_json = await response.json()

                return response_json['results']

    async def get_received_orders(self, is_pagination=None, page=None, limit=None):
        orders = await self.orders()

        returning_orders = []

        for order in orders:
            if order['status'] in ['delivered', 'cancelled']:
                returning_orders.append(order)

        if is_pagination:
            return returning_orders

        start_index = (page - 1) * limit
        end_index = start_index + limit

        return returning_orders[start_index:end_index]

    async def get_order(self, order_id: int, is_active: bool = None):
        orders = await self.orders()

        if is_active:
            orders = await self.orders(is_active=True)

        for order in orders:
            if order['id'] == order_id:
                return order

        return None

    async def order_formation(self, data: dict):
        async with ClientSession(headers=self.headers) as session:
            async with session.post(url=f'{self.url}/order/formation/', json=data) as response:

                if response.status != 200:
                    return None

                return True

    async def cancel_order(self, order_id: int):
        async with ClientSession(headers=self.headers) as session:
            async with session.post(url=f'{self.url}/order/{order_id}/cancel/') as response:
                return True

    async def create_order_food_in_stock(self, data: dict):
        print(self.headers)
        async with ClientSession(headers=self.headers) as session:
            async with session.post(url=f"{self.url}/order/food_in_stock/", json=data) as response:
                print(response)
                print(response.status)
                print(response.content)
                print(await response.text())

                if response.status > 300:
                    return None

                return True

    async def get_order_items(self):
        async with ClientSession(headers=self.headers) as session:
            async with session.get(url=f'{self.url}/order/item/') as response:
                return await response.json()

    async def get_order_item(self, item_id: int):
        async with ClientSession(headers=self.headers) as session:
            async with session.get(url=f'{self.url}/order/item/{item_id}') as response:
                return await response.json()

    async def create_order_item(self, data: dict):
        async with ClientSession(headers=self.headers) as session:
            async with session.post(url=f'{self.url}/order/item/', json=data) as response:

                if response.status != 201:
                    return None

                return True

    async def update_order_item_count(self, item_id: int, data: dict):
        async with ClientSession(headers=self.headers) as session:
            async with session.patch(url=f'{self.url}/order/item/{item_id}/', json=data) as response:
                return await response.json()

    async def delete_order_item(self, item_id: int):
        async with ClientSession(headers=self.headers) as session:
            async with session.delete(url=f'{self.url}/order/item/{item_id}/') as response:

                if response.status != 204:
                    return None

                return True
