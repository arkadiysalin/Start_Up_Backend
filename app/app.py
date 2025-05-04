import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.routers import *
from starlette.responses import FileResponse 
from redis import Redis
from scalar_fastapi import get_scalar_api_reference
from fastapi.staticfiles import StaticFiles


app = FastAPI(tags=["Freestyle BOT"])
# Обработчик для статических файлов
# app.mount("/images", StaticFiles(directory="static"), name="images")

origins = [
    "http://localhost:3000",
    "https://skyrodev.ru",
    "http://0.0.0.0:8000",
    "https://backend.skyrodev.ru",
    "http://127.0.0.1:3000",
    "https://kimchistop.ru",
    "https://api.kimchistop.ru",
    "https://food-bot-site.netlify.app"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)


app.include_router(router)

@app.get("/scalar")
async def scalar():
    return get_scalar_api_reference(
        title="Scalar API",
        openapi_url=app.openapi_url
    )
 
UPLOAD_DIR = os.path.abspath("uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)   
# app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")
