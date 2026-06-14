from app.services.telegram.setup import telegram

async def check_language(command, chat_id, user, update):
        print("Checking Language...")
        if not user["language"]:
            user["state"] = "choose_language" 
            user["prev_command"] = command
            user["prev_update"] = update
            language_message = (
                "🌐 Choose language:\n\n"
                "🇪🇹 አማርኛ: /am\n"
                "🇸🇦 العربية: /ar"
            )

            await telegram.send_message(chat_id, language_message)
            return True
        return False