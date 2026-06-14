from app.services.telegram.setup import telegram

@telegram.command("/am")
async def am(update, user):
    print("Obeying AM (አማረኛ) Command...")
    chat_id = update["message"]["chat"]["id"]
    user["language"] = "am"
    await telegram.send_message(chat_id=chat_id, text="ቋንቋ ወደ አማርኛ ተቀይሯል")

@telegram.command("/ar")
async def am(update, user):
    print("Obeying AR (العربية) Command...")
    chat_id = update["message"]["chat"]["id"]
    user["language"] = "ar"
    await telegram.send_message(chat_id=chat_id, text="تم تغيير اللغة الى العربية")
