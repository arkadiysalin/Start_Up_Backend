from fastapi import APIRouter, HTTPException

router = APIRouter()

# Простейшее in-memory хранилище для демонстрации
user_favorites = {}

@router.post("/add")
async def add_to_favorites(user_id: int, product_id: int):
    favorites = user_favorites.get(user_id, [])
    if product_id in favorites:
        raise HTTPException(status_code=400, detail="Товар уже в избранном")
    favorites.append(product_id)
    user_favorites[user_id] = favorites
    return {"user_id": user_id, "favorites": favorites}

@router.get("/")
async def get_favorites(user_id: int):
    """
    Возвращает список избранных товаров для пользователя.
    """
    favorites = user_favorites.get(user_id, [])
    return {"user_id": user_id, "favorites": favorites}

@router.delete("/remove")
async def remove_from_favorites(user_id: int, product_id: int):
    favorites = user_favorites.get(user_id)
    if not favorites or product_id not in favorites:
        raise HTTPException(status_code=404, detail="Товар не найден в избранном")
    favorites.remove(product_id)
    user_favorites[user_id] = favorites
    return {"user_id": user_id, "favorites": favorites}

@router.patch("/update")
async def update_favorite(user_id: int, product_id: int):
    """
    Переключает состояние товара между "избранным" и "неизбранным".
    """
    favorites = user_favorites.get(user_id, [])
    if product_id in favorites:
        # Если товар уже в избранном, удаляем его
        favorites.remove(product_id)
    else:
        # Если товара нет в избранном, добавляем его
        favorites.append(product_id)
    user_favorites[user_id] = favorites
    return {"user_id": user_id, "favorites": favorites}