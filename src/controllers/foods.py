from aiohttp import ClientSession
from typing import Optional
from src.helpers.utils import parse_text_to_html

from src.helpers.environ import BASE_URL


class FoodController:
    def __init__(self):
        self.url = f'{BASE_URL}/food'
        self.headers = self.headers = {'Accept': 'application/json'}

    async def get_foods_for_order(self) -> Optional[dict]:
        async with ClientSession(headers=self.headers) as session:
            async with session.get(f'{self.url}/') as response:
                returning_data = await response.json()

                if len(returning_data['results']) == 0:
                    return None

                return returning_data['results']

    async def get_one_food(self, food_id):
        order_foods = await self.get_foods_for_order()

        for food in order_foods:
            if food['id'] == food_id:
                soup = parse_text_to_html(food['description'])
                food['description'] = soup
                return food

        return None

    async def in_stock(self):
        async with ClientSession(headers=self.headers) as session:
            async with session.get(f'{self.url}/in_stock/') as response:
                response_json = await response.json()

                if response.status != 200 or len(response_json) == 0:
                    return None

                return response_json['results']

    async def get_one_from_stock(self, food_id):
        stock_foods = await self.in_stock()

        for item in stock_foods:
            if item['food']['id'] == food_id:
                soup = parse_text_to_html(item['food']['description'])
                item['food']['description'] = soup
                return item

        return None
