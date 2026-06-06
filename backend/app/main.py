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
    text = update["message"]["text"] if "text" in update["message"] else update["message"].get("caption", "")
    chat_id = update["message"]["chat"]["id"]

    if text.startswith("/readqr"):
        photo = update["message"]["photo"][-1]
        file_id = photo["file_id"]

        img_response = await telegram.download_file(file_id=file_id)
        photo_bytes = img_response.content
        response = await upload_qr_image(image_bytes=photo_bytes)

        pending_actions[chat_id] = response.get("data", "Could not read QR code")
        
        await telegram.send_message(
            chat_id=chat_id,
            text=(
                f"Name: {pending_actions[chat_id].get('seller', 'N/A')}\n"
                f"Amount: {pending_actions[chat_id].get('total', 'N/A')}\n"
                f"Date: {pending_actions[chat_id].get('timestamp', 'N/A')}\n"
                f"VAT No: {pending_actions[chat_id].get('vat_number', 'N/A')}\n\n"
            ),
            reply_markup={
                "inline_keyboard": [
                    [
                        {"text": "✅ Confirm", "callback_data": "confirm"},
                        {"text": "✏️ Edit", "callback_data": "edit"},
                        {"text": "❌ Cancel", "callback_data": "cancel"}
                    ]
                ]
            }
        )
        
        if update.get("callback_query"):
            callback_data = update["callback_query"]["data"]
            if callback_data == "confirm":
                # Save to DB or perform action
                expense = await create_purchase(ExpenseModel(
                    data=pending_actions.get("timestamp"),
                    contact_name=pending_actions.get("seller"),
                    tax_reg_no=pending_actions.get("vat_number"),
                    amount=float(pending_actions("total"))
                    
                ))
                await telegram.send_message(
                    chat_id=chat_id,
                    text=f"✅ Expense with id '{expense.expense_id}' created."
                )


                print(f"User confirmed data: {pending_actions[chat_id]}")
                del pending_actions[chat_id]
            elif callback_data == "edit":
                # Ask user for new input
                print(f"User wants to edit data: {pending_actions[chat_id]}")
            elif callback_data == "cancel":
                print(f"User cancelled action for data: {pending_actions[chat_id]}")
                del pending_actions[chat_id]
        # Call internal logic/API here

    return {"ok": True}


