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

from decimal import Decimal


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

def extract_purchase_data(text: str) -> dict:
    """
    Extract purchase data from text like:

    Name: مؤسسة بحر التوابل للمواد الغذائيه
    Amount: 5520.0
    Date: 2026-04-07T08:25:08Z
    VAT No: 311964379200003
    """
    fields = {}

    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()

    return {
        "name": fields.get("Name"),
        "amount": float(fields["Amount"]) if fields.get("Amount") else None,
        "date": fields.get("Date"),
        "vat_no": fields.get("VAT No"),
    }

# @app.on_event("startup")
# def oxygen():
#     start_scheduler()

telegram = TelegramService(bot_token=TELEGRAM_BOT_TOKEN)
pending_actions = {}
@app.post("/telegram/webhook")
async def webhook(request: Request):
    update = await request.json()
    print(f"🔵 Received Telegram update: {update}")

    message = update.get("message")
    callback = update.get("callback_query")

    chat_id = None
    text = ""

    # ---------------- MESSAGE FLOW ----------------
    if message:
        chat_id = message["chat"]["id"]
        text = message.get("text") or message.get("caption") or ""

        AR_QR_INVOICE = "صورة + /qrcode (إدخال الفاتورة عبر QR)"
        AR_IMG_INVOICE = "صورة + /enter (إدخال الفاتورة عبر صورة)"

        AM_QR_INVOICE = "ፎቶ + /qrcode (በQR ኮድ የኢንቮይስ ግቤት)"
        AM_IMG_INVOICE = "ፎቶ + /enter (በፎቶ የኢንቮይስ ግቤት)"

        if text.startswith("/start"):
            await telegram.send_message(
                chat_id=chat_id,
                text=(
                    "Arabic:\n"
                    "صورة + /qrcode - إدخال الفاتورة عبر QR\n"
                    "صورة + /enter - إدخال الفاتورة عبر صورة\n\n"
                    "Amharic:\n"
                    "ፎቶ + /qrcode - በQR ኮድ ግቤት\n"
                    "ፎቶ + /enter - በፎቶ ግቤት"
                )
            )

    # ---------------- CALLBACK FLOW ----------------
    elif callback:
        chat_id = callback["message"]["chat"]["id"]
        callback_data = callback["data"]
        
        if callback_data == "confirm":
            pass
        elif callback_data == "edit":
            pass
        elif callback_data == "cancel":
            pass
    return {"ok": True}