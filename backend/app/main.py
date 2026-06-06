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

from app.controllers.image_controllers import upload_qr_image
from app.controllers.expenses_controllers import create_purchase

from app.services.telegram_services import TelegramService

from app.models.expenses_models import ExpenseModel

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

telegram = TelegramService(bot_token=TELEGRAM_BOT_TOKEN)
pending_actions = {}
@app.post("/telegram/webhook")
async def webhook(request: Request):
    update = await request.json()
    print(f"Received Telegram update: {update}")

    message = update.get("message")
    callback = update.get("callback_query")

    chat_id = None
    text = ""

    # ---------------- MESSAGE FLOW ----------------
    if message:
        chat_id = message["chat"]["id"]
        text = message.get("text") or message.get("caption") or ""

        if text.startswith("/readqr"):
            photo = message["photo"][-1]
            file_id = photo["file_id"]

            photo_bytes = await telegram.download_file(file_id=file_id)
            response = await upload_qr_image(image_bytes=photo_bytes)

            data = response.get("data", {})
            pending_actions[chat_id] = data

            await telegram.send_message(
                chat_id=chat_id,
                text=(
                    f"Name: {data.get('seller', 'N/A')}\n"
                    f"Amount: {data.get('total', 'N/A')}\n"
                    f"Date: {data.get('timestamp', 'N/A')}\n"
                    f"VAT No: {data.get('vat_number', 'N/A')}\n"
                ),
                reply_markup={
                    "inline_keyboard": [
                        [
                            {"text": "✅ Confirm", "callback_data": "confirm"},
                            {"text": "✏️ Edit", "callback_data": "edit"},
                            {"text": "❌ Cancel", "callback_data": "cancel"},
                        ]
                    ]
                },
            )

    # ---------------- CALLBACK FLOW ----------------
    elif callback:
        chat_id = callback["message"]["chat"]["id"]
        callback_data = callback["data"]

        data = pending_actions.get(chat_id)

        if callback_data == "confirm":
            expense = await create_purchase(ExpenseModel(
                data=data.get("timestamp"),
                contact_name=data.get("seller"),
                tax_reg_no=data.get("vat_number"),
                amount=float(data.get("total", 0)),
            ))

            await telegram.send_message(
                chat_id=chat_id,
                text=f"✅ Expense created: {expense.expense_id}"
            )

            pending_actions.pop(chat_id, None)

        elif callback_data == "edit":
            print(f"Edit requested: {data}")

        elif callback_data == "cancel":
            print(f"Cancelled: {data}")
            pending_actions.pop(chat_id, None)

    return {"ok": True}