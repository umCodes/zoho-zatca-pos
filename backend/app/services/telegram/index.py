import httpx
import json

class Telegram:
    def __init__(self, bot_token: str, langs: list[str]):
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.bot_token = bot_token
        self.langs = langs
        self.commands = {}
        self.states = {}
        self.users = {} 

    def set_langs(self, langs: list[str]):
        self.langs = langs

    def command(self, name):
        def decorator(func):
            self.commands[name] = func
            return func
        return decorator


    def state(self, name):
        def decorator(func):
            self.states[name] = func
            return func
        return decorator
    
    
    async def download_file(self, file_id: str) -> bytes:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Get file path
            res = await client.get(
                f"{self.base_url}/getFile",
                params={"file_id": file_id},
            )
            res.raise_for_status()
            file_path = res.json()["result"]["file_path"]

            # 2. Download file directly
            file_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            file_res = await client.get(file_url)
            file_res.raise_for_status()

            return file_res.content
    
    async def send_message(self, chat_id, text):
        # here you call Telegram API
        async with httpx.AsyncClient() as client:
            await client.post(f"{self.base_url}/sendMessage", json={"chat_id": chat_id, "text": text})

    async def send_image(self, chat_id, image_path):
            url = f"{self.base_url}/sendPhoto"

            async with httpx.AsyncClient() as client:
                with open(image_path, "rb") as file:
                    files = { "photo": file }
                    data = { "chat_id": chat_id }
                    await client.post(url, data=data, files=files)


    async def dispatch(self, update):
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", None)
        photo = message.get("photo", None)


        # create user if not exists
        if chat_id not in self.users:
            self.users[chat_id] = {
                "language": None,
                "state": None
            }


        user = self.users[chat_id]

        print("- User Keys: ", user.keys())
        print("- Update Keys: ", update.keys())
        # 1. Check active state first
        if user["state"]:
            handler = self.states.get(user["state"])
            if handler:
                return await handler(update,user)
        

        if photo:
            handler = self.commands.get("photo")
            await handler(update,user)
            return
        
        # 2. Normal commands
        handler = self.commands.get(text)
        if handler:
            return await handler(update,user)
        
        # 3. Unknown message
        await self.send_message(chat_id, "Unknown command")











