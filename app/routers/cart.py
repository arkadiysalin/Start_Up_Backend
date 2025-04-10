from fastapi import APIRouter, HTTPException

router = APIRouter()

# Хранилище для корзин: каждый user_id имеет словарь, где ключ - product_id, значение - quantity
user_carts = {}

@router.post("/add")
async def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    cart = user_carts.get(user_id, {})
    if product_id in cart:
        cart[product_id] += quantity  # увеличиваем количество товара
    else:
        cart[product_id] = quantity   # добавляем товар с начальным количеством
    user_carts[user_id] = cart
    return {"user_id": user_id, "cart": cart}

@router.get("/data")
async def get_cart(user_id: int):
    cart = user_carts.get(user_id, {})
    return {"user_id": user_id, "cart": cart}

@router.delete("/remove")
async def remove_from_cart(user_id: int, product_id: int, quantity: int = 1):
    cart = user_carts.get(user_id)
    if not cart or product_id not in cart:
        raise HTTPException(status_code=404, detail="Товар не найден в корзине")
    if cart[product_id] > quantity:
        cart[product_id] -= quantity  # уменьшаем количество товара
    else:
        del cart[product_id]  # удаляем товар, если количество становится 0 или меньше
    user_carts[user_id] = cart
    return {"user_id": user_id, "cart": cart}