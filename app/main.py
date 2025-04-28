import uvicorn
import asyncio

from admin.bot import check_for_new_orders as check_redis_for_new_data
from admin.bot import dp
from admin.bot import bot

async def bott():
    print("Bot started")
    await dp.start_polling(bot)
    

async def fastapi():
    config = uvicorn.Config("app:app", host="0.0.0.0", port=8001, log_level="info", reload=True, ws="websockets")
    server = uvicorn.Server(config)
    await server.serve()
    print("FastAPI started")

async def redis():
    await check_redis_for_new_data()
    print("Redis started")

async def main():
    await asyncio.gather(bott(), fastapi(), redis())






if __name__ == "__main__":
    asyncio.run(main())