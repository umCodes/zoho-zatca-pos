from pathlib import Path
from app.services.telegram.setup import telegram
from app.services.telegram.utils.check_lang import check_language 


@telegram.command("/start")
async def start(update, user):
    print("Obeying Start Command...")
    try:
            
        chat_id = update["message"]["chat"]["id"]
        
        is_language_missing = await check_language("/start", chat_id, user, update)
        if is_language_missing:
            return        
        
        responses = {
            "am": "የደረሰኝ QR ኮድ ፎቶ ይላኩ።",
            "ar":  "\u200Fارسل رمز ال\"QR\" الخاص بالفاتورة."
        }
        BASE_DIR = Path(__file__).resolve().parents[4]  # adjust if needed
        IMAGE_PATH = BASE_DIR / "uploads" / "qr.jpg"

        await telegram.send_image(chat_id=chat_id, image_path=IMAGE_PATH)
        await telegram.send_message(chat_id=chat_id, text=responses[user["language"]])

    except Exception as e:
        print("Error: ", e)


