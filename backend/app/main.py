from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import pdf
from app.api.routes import invoices, items, check_password, health, expenses, vendors, images
from app.core.config import ENV, FRONTEND_DOMAIN

from app.middlewares.token_refresh import token_refresh_middleware
from app.middlewares.validate_password import validate_password

from app.db.database import create_tables 

# from app.cron.oxygen import start_scheduler

from app.core.config import TELEGRAM_BOT_TOKEN

import httpx

import sys
import os

print("Python version:", sys.version, file=sys.stderr)
print("Current working directory:", os.getcwd(), file=sys.stderr)

app = FastAPI()

create_tables()




if ENV == "prod":
    origins = [FRONTEND_DOMAIN]
else:
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(validate_password)
app.middleware("http")(token_refresh_middleware)

app.include_router(health.router)
app.include_router(check_password.router)
app.include_router(invoices.router)
app.include_router(expenses.router)
app.include_router(vendors.router)
app.include_router(items.router)
app.include_router(pdf.router)
app.include_router(images.router)


# @app.on_event("startup")
# def oxygen():
#     start_scheduler()



@app.post("/telegram/webhook")
async def webhook(request: Request):
    update = await request.json()
    text = update["message"]["text"]
    chat_id = update["message"]["chat"]["id"]

    if text.startswith("/weather"):
        city = text.replace("/weather", "").strip()

        # Call internal logic/API here

        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": f"Weather for {city}: Sunny"
                }
            )

    return {"ok": True}