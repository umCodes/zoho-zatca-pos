from app.services.telegram.setup import telegram

@telegram.state("choose_language")
async def choose_language(update, user):
    print("Applying Choose Language State...")
    if not update["message"].get("text") :
        return

    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"]
    chosen_lang = text.lstrip("/")
    languages = telegram.langs


    if chosen_lang not in languages:
        await telegram.send_message(chat_id, "Invalid language")
        return

    

    user["language"] = chosen_lang
    user["state"] = None

    handler = telegram.commands.get(user["prev_command"])
    if handler:
        return await handler(user["prev_update"],user)
