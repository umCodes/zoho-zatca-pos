from datetime import datetime
import httpx
from app.core.config import CLIENT_ID, CLIENT_SECRET, get_settings

auth_state = {
    "access_token": get_settings()["access_token"],
    "expires_at": 0
}

async def refresh_token_if_needed():
    if auth_state["expires_at"] > datetime.now().timestamp():
        return

    async with httpx.AsyncClient() as client:
        params = {
            "refresh_token": get_settings()["refresh_token"],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": "http://localhost:3000/",
            "grant_type": "refresh_token"
        }

        res = await client.post(
            "https://accounts.zoho.sa/oauth/v2/token",
            data=params
        )

        data = res.json()

        auth_state["access_token"] = data["access_token"]
        auth_state["expires_at"] = datetime.now().timestamp() + 3600

        print("🦖 Zoho Tokens Refreshed")
