from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from auth.database import get_async_session
from models.models import Food

router = APIRouter()

# Хранилище для корзин: каждый user_id имеет словарь, где ключ - product_id, значение - quantity
user_carts = {}

@router.post("/add")
async def add_to_cart(user_id: int, product_id: int, quantity: int = 1, db: Session = Depends(get_async_session)):
    cart = user_carts.get(user_id, {})
    if product_id in cart:
        cart[product_id] += quantity  # увеличиваем количество товара
    else:
        cart[product_id] = quantity   # добавляем товар с начальным количеством
    user_carts[user_id] = cart
    return {"user_id": user_id, "cart": cart}

@router.get("/data")
async def get_cart(user_id: int, db: Session = Depends(get_async_session)):
    cart = user_carts.get(user_id, {})
    response = []

    for product_id, quantity in cart.items():
        stmt = select(Food).where(Food.id == product_id)
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()  # Получаем один объект или None

        if product:
            response.append({
                "id": product.id,
                "quantity": quantity,
                "price": product.price,
                "name": product.foodName,
                "image": product.image,
                "description": product.description,
            })

    return {"user_id": user_id, "cart": response}

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