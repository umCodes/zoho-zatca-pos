from fastapi import APIRouter, Request
from app.services.telegram.setup import telegram

router = APIRouter()

@router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    update = await request.json()
    await telegram.dispatch(update=update)
    return {
        "ok": True, 
        "message": "ok"
    }