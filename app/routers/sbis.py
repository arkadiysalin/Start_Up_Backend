import base64
import re
import requests
from pydantic import AnyUrl, BaseModel
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime
from fastapi import APIRouter
import logging
from typing import Union
logging.basicConfig(level=logging.INFO)
from fastapi import UploadFile, Request, HTTPException
import os
import json
from typing import Optional
from fastapi import APIRouter, Query, Depends
import requests
import base64
import json
import asyncio
sbisRouter = APIRouter()


IMAGE_DIR = "/images"

load_dotenv()
APP_CLIENT_ID = os.getenv("APP_CLIENT_ID")
APP_SECRET = os.getenv("APP_SECRET")
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")

class TokenValidation(BaseModel):
    access_token: str
    sid: str
    token: str
    
class AuthorizationData(BaseModel):
    app_client_id: str
    app_secret: str
    app_secret_key: str
    

class FoodsRequest(BaseModel):
    pointId: int
    priceListId: int
    withBalance: Union[bool, None] = True
    withBarcode: Union[bool, None] = True
    onlyPublished: Union[bool, None] = True
    pageSize: Union[str, None] = '2000'
    noStopList: Union[bool, None] = True
    
class SBIService():
    @staticmethod
    async def get_token(data: AuthorizationData) -> TokenValidation:
        url = 'https://online.sbis.ru/oauth/service/'
        json={"app_client_id": f'{data.app_client_id}',"app_secret": f"{data.app_secret}","secret_key": f"{data.app_secret_key}"}
        url = 'https://online.sbis.ru/oauth/service/'    
        response = requests.post(url, json=json)
        response.encoding = 'utf-8'
        return TokenValidation(**response.json())

    @staticmethod
    async def get_point_id(token: TokenValidation) -> dict:
        parameters = {
        'withPhones': 'true',
        'withPrices': 'true'
        }
        url = 'https://api.sbis.ru/retail/point/list?'  
        headers = {
        "X-SBISAccessToken": f"{token.access_token}"
        }  
        response = requests.get(url, params=parameters, headers=headers)
        return response.json()

    @staticmethod
    async def get_price_lists(token: TokenValidation, point_id: int) -> dict:
        parameters = {
        'pointId': point_id,
        'actualDate': f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        }
        url = 'https://api.sbis.ru/retail/nomenclature/price-list?'  
        headers = {
        "X-SBISAccessToken": f"{token.access_token}"
        }  
        response = requests.get(url, params=parameters, headers=headers)
        return response.json()
    
    @staticmethod
    async def get_foods(request: FoodsRequest, token: TokenValidation) -> dict:
        parameters = request.model_dump()
        url = 'https://api.sbis.ru/retail/nomenclature/list?'
        headers = {
                "X-SBISAccessToken": f"{token.access_token}"
        }
        response = requests.get(url, params = parameters, headers = headers)
        return response.json()
    @staticmethod
    async def get_image(token, image, name):
        url = f"https://api.sbis.ru/retail/img"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "image/*",
            "X-SBISAccessToken": f"{token.access_token}"
        }
        replaced = image.replace("/img?params=", "")
        params = {
            "params": replaced
        }
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            try:
                from PIL import Image
                from io import BytesIO

                image_data = BytesIO(response.content)
                img = Image.open(image_data)
                img.save(f"images/{name}.png")
                return f"Image saved as {name}.png"
            except Exception as e:
                return f"Failed to process image: {str(e)}"
        else:
            return f"Error while reading response: {response.status_code}, {response.text}"
  
sbis = SBIService()

@sbisRouter.post('/register')
async def register():
    token: TokenValidation = await sbis.get_token(AuthorizationData(app_client_id=APP_CLIENT_ID, app_secret=APP_SECRET, app_secret_key=APP_SECRET_KEY))
    poinID: dict = await sbis.get_point_id(token)
    menu: dict = await sbis.get_price_lists(token, poinID['salesPoints'][0]['id'])
    return poinID

@sbisRouter.get("/categories1")
async def get_categories():
    token: TokenValidation = await sbis.get_token(AuthorizationData(app_client_id=APP_CLIENT_ID, app_secret=APP_SECRET, app_secret_key=APP_SECRET_KEY))
    poinID: dict = await sbis.get_point_id(token)
    menu: dict = await sbis.get_price_lists(token, poinID['salesPoints'][0]['id'])
    foods: list = await sbis.get_foods(FoodsRequest(pointId=poinID['salesPoints'][0]['id'], priceListId=menu["priceLists"][1]["id"]), token)

    return  foods

@sbisRouter.get("/categories")
async def get_categories():
    token: TokenValidation = await sbis.get_token(
        AuthorizationData(
            app_client_id=APP_CLIENT_ID,
            app_secret=APP_SECRET,
            app_secret_key=APP_SECRET_KEY
        )
    )
    
    # Получаем список точек продаж и прайс-листов
    poinID: dict = await sbis.get_point_id(token)
    menu: dict = await sbis.get_price_lists(token, poinID['salesPoints'][0]['id'])
    
    # Получаем список продуктов
    foods: dict = await sbis.get_foods(
        FoodsRequest(
            pointId=poinID['salesPoints'][0]['id'],
            priceListId=menu["priceLists"][1]["id"]
        ),
        token
    )
    
    # Фильтруем только те товары, у которых hierarchicalParent равен None
    categories = [
        item for item in foods["nomenclatures"] if item.get("hierarchicalParent") == 2110
    ]
    
    return categories




# @sbisRouter.get("/products/kitchen")
# async def get_kitchen_products():
#     # Получение токена
#     token: TokenValidation = await sbis.get_token(
#         AuthorizationData(
#             app_client_id=APP_CLIENT_ID, 
#             app_secret=APP_SECRET, 
#             app_secret_key=APP_SECRET_KEY
#         )
#     )
    
#     # Получение точки продаж и списка цен
#     poinID: dict = await sbis.get_point_id(token)
#     menu: dict = await sbis.get_price_lists(token, poinID['salesPoints'][0]['id'])
    
#     # Запрос списка товаров
#     foods: dict = await sbis.get_foods(
#         FoodsRequest(
#             pointId=poinID['salesPoints'][0]['id'], 
#             priceListId=menu["priceLists"][3]["id"],
#             withBalance=True,  # Убедитесь, что вы получаете все товары
#             withBarcode=False,
#             onlyPublished=False,
#         ),
#         token
#     )

#     found_foods: list = []
#     for el in foods['nomenclatures']:
#         if el["cost"] != None:
#             found_foods.append(el)

#     # return {"kitchen_products": kitchen_products}
#     return found_foods

# @sbisRouter.get("/sbis-products")
# async def download_kitchen_images():
#     token: TokenValidation = await sbis.get_token(
#         AuthorizationData(
#             app_client_id=APP_CLIENT_ID,
#             app_secret=APP_SECRET,
#             app_secret_key=APP_SECRET_KEY
#         )
#     )

#     # Получаем список точек продаж и прайс-листов
#     poinID: dict = await sbis.get_point_id(token)
#     menu: dict = await sbis.get_price_lists(token, poinID['salesPoints'][0]['id'])

#     # Получаем список продуктов
#     foods: dict = await sbis.get_foods(
#         FoodsRequest(
#             pointId=poinID['salesPoints'][0]['id'],
#             priceListId=menu["priceLists"][3]["id"],
#             withBalance=True,
#             withBarcode=False,
#             onlyPublished=False,
#         ),
#         token
#     )

#     # Создаем семафор для ограничения количества одновременных запросов
#     semaphore = asyncio.Semaphore(10)

#     downloaded_count = 0  # Счётчик загруженных изображений
#     max_downloads = 20  # Лимит на количество скачиваний

#     def decode_base64_param(encoded_param: str):
#         """Декодирует параметр base64 и извлекает PhotoURL"""
#         # Декодируем строку base64
#         decoded_bytes = base64.b64decode(encoded_param)
#         decoded_str = decoded_bytes.decode('utf-8')
        
#         # Парсим JSON строку
#         decoded_json = json.loads(decoded_str)
#         return decoded_json.get('PhotoURL')

#     async def get_image_url(item, idx):
#         nonlocal downloaded_count  # Чтобы обновлять счётчик в функции
#         # Проверяем, есть ли изображения у продукта
#         if 'images' in item and item['images'] and downloaded_count < max_downloads:
#             image_url = item['images'][0]
#             encoded_param = image_url.split('?params=')[-1]  # Извлекаем часть после ?params=
#             photo_url = decode_base64_param(encoded_param)  # Декодируем base64 и извлекаем PhotoURL
            
#             if photo_url:
#                 downloaded_count += 1  # Увеличиваем счётчик
#                 return {
#                     "id": item["id"],
#                     "name": item["name"],
#                     "status": "Image available",
#                     "image": photo_url,  # Ссылка на изображение
#                     "price": item["cost"],
#                     "description": item["description_simple"],
#                     "category": item["hierarchicalParent"],
#                 }
#             else:
#                 return {
#                     "product": item["name"],
#                     "status": "No image found"
#                 }

#     tasks = []
#     for idx, item in enumerate(foods['nomenclatures']):
#         if downloaded_count >= max_downloads:
#             break  # Останавливаем цикл, если достигнут лимит
#         if item.get("hierarchicalParent") != 2382:  # Фильтруем товары
#             tasks.append(get_image_url(item, idx))

#     download_results = await asyncio.gather(*tasks)
#     filtered_results = [result for result in download_results if result is not None]
#     return filtered_results


# Предполагается, что у вас есть уже настроенные зависимости для токена и моделе

@sbisRouter.get("/sbis-products")
async def get_sbis_products(
    categoryId: Optional[int] = Query(None, description="ID категории для фильтрации товаров"),
):
    token: TokenValidation = await sbis.get_token(
        AuthorizationData(
            app_client_id=APP_CLIENT_ID,
            app_secret=APP_SECRET,
            app_secret_key=APP_SECRET_KEY
        )
    )

    # Получаем список точек продаж и прайс-листов
    point_id_data: dict = await sbis.get_point_id(token)
    point_id = point_id_data['salesPoints'][0]['id']
    menu: dict = await sbis.get_price_lists(token, point_id)

    # Получаем список продуктов
    foods: dict = await sbis.get_foods(
        FoodsRequest(
            pointId=point_id,
            priceListId=menu["priceLists"][3]["id"],
            withBalance=True,
            withBarcode=False,
            onlyPublished=False,
        ),
        token
    )

    def decode_base64_param(encoded_param: str):
        """Декодирует параметр base64 и извлекает PhotoURL"""
        decoded_bytes = base64.b64decode(encoded_param)
        decoded_str = decoded_bytes.decode('utf-8')
        decoded_json = json.loads(decoded_str)
        return decoded_json.get('PhotoURL')

    async def process_product(item):
        # Проверяем, есть ли изображения у продукта
        if 'images' in item and item['images']:
            encoded_param = item['images'][0].split('?params=')[-1]
            photo_url = decode_base64_param(encoded_param)

            if photo_url:  # Если изображение успешно декодировано
                return {
                    "id": item["id"],
                    "name": item["name"],
                    "status": "Image available",
                    "image": photo_url,
                    "price": item["cost"],
                    "description": item.get("description_simple"),
                    "category": item["hierarchicalParent"],
                }
        return None  # Пропускаем товары без изображений

    # Фильтруем товары: исключаем категорию 2382 (электронные сигареты)
    filtered_items = [
        item for item in foods["nomenclatures"] 
        if (categoryId is None or item.get("hierarchicalParent") == categoryId)
        and item.get("hierarchicalParent") != 2382  # Исключаем категорию 2382
    ]

    # Асинхронно обрабатываем товары
    tasks = [process_product(item) for item in filtered_items]
    processed_items = await asyncio.gather(*tasks)

    # Исключаем None (товары без изображений)
    processed_items = [item for item in processed_items if item is not None]

    return processed_items




@sbisRouter.get("/sbis-product/{product_id}")
async def get_product_by_id(product_id: int):
    token: TokenValidation = await sbis.get_token(
        AuthorizationData(
            app_client_id=APP_CLIENT_ID,
            app_secret=APP_SECRET,
            app_secret_key=APP_SECRET_KEY
        )
    )

    # Получаем список точек продаж и прайс-листов
    poinID: dict = await sbis.get_point_id(token)
    menu: dict = await sbis.get_price_lists(token, poinID['salesPoints'][0]['id'])

    # Получаем список продуктов
    foods: dict = await sbis.get_foods(
        FoodsRequest(
            pointId=poinID['salesPoints'][0]['id'],
            priceListId=menu["priceLists"][3]["id"],
            withBalance=True,
            withBarcode=False,
            onlyPublished=False,
        ),
        token
    )

    def decode_base64_param(encoded_param: str):
        decoded_bytes = base64.b64decode(encoded_param)
        decoded_str = decoded_bytes.decode('utf-8')
        
        # Парсим JSON строку
        decoded_json = json.loads(decoded_str)
        return decoded_json.get('PhotoURL')

    # Ищем товар с заданным id
    product = next((item for item in foods['nomenclatures'] if item['id'] == product_id), None)
    
    if product:
        # Проверяем, есть ли изображения у продукта
        if 'images' in product and product['images']:
            image_url = product['images'][0]
            # Извлекаем параметр из URL
            encoded_param = image_url.split('?params=')[-1]  # Извлекаем часть после ?params=
            photo_url = decode_base64_param(encoded_param)  # Декодируем base64 и извлекаем PhotoURL
        else:
            photo_url = None

        # Возвращаем информацию о товаре
        return {
            "id": product["id"],
            "name": product["name"],
            "status": "Image available",
            "image": photo_url,
            "price": product["cost"],
            "description": product.get("description_simple"),
            "category": product["hierarchicalParent"],
        }
    else:
        # Если товар не найден
        return {
            "status": "Product not found",
            "id": product_id
        }
