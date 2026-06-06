import httpx
from typing import Any, Dict, Optional


class TelegramService:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def get_file_path(self, file_id: str) -> str:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.base_url}/getFile", params={"file_id": file_id})
            res.raise_for_status()
            return res.json()["result"]["file_path"]

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
    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "text": text}

        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with httpx.AsyncClient() as client:
            res = await client.post(f"{self.base_url}/sendMessage", json=payload)
            res.raise_for_status()
            return res.json()