import httpx
from app.core.config import ORGANIZATION_ID, ZOHO_BASE_URL
from app.services.zoho.auth import refresh_token_if_needed, auth_state


class ZohoClient:
    def __init__(self, base_url, organization_id):
        self.base_url = base_url
        self.organization_id = organization_id

    async def request(self, path, method = "GET", params = {}, include_org_id: bool = False, **kwargs):
        await refresh_token_if_needed()
        
        url = f"{self.base_url}{path}"
    
        headers = {
            "Authorization": f"Bearer {auth_state["access_token"]}"
        }

        if include_org_id:
            params["organization_id"] = self.organization_id

        async with httpx.AsyncClient() as client:

            return await client.request(
                url=url,
                method=method,
                headers=headers,
                params=params,
                **kwargs
            )
        
zoho_client = ZohoClient(ZOHO_BASE_URL, ORGANIZATION_ID)