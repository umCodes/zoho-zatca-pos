import httpx
from app.core.auth import auth_state
from app.core.config import get_settings

BASE_URL = "https://www.zohoapis.sa/books/v3"

def get_headers():
    return {
        "Authorization": f"Zoho-oauthtoken {auth_state['access_token']}"
    }

def get_params():
    return {
        "organization_id": get_settings()["organization_id"]
    }


async def zoho_get(path: str, params:  dict = None):
    merged_params = {**get_params(), **(params or {})}  # merge safely
    print(f"Making GET request to {BASE_URL}{path} with params: {merged_params}")
    async with httpx.AsyncClient() as client:
        return await client.get(
            f"{BASE_URL}{path}",
            headers=get_headers(),
            params=merged_params
        )


async def zoho_post(path: str, payload: dict = {}):
    async with httpx.AsyncClient() as client:
        return await client.post(
            f"{BASE_URL}{path}",
            headers={
                **get_headers(),
                "content-type": "application/json"
            },
            params=get_params(),
            json=payload
        )