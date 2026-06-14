import httpx
from fastapi import Response
from app.core.auth import auth_state
from app.core.config import get_settings

async def get_pdf(invoice_id: str):
    url = f"https://www.zohoapis.sa/books/v3/invoices/{invoice_id}"

    params = {
        "organization_id": get_settings()["organization_id"],
        "accept": "pdf",
        "print": "true"
    }

    headers = {
        "Authorization": f"Zoho-oauthtoken {auth_state['access_token']}"
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params, headers=headers)

    return Response(
        content=res.content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=invoice_{invoice_id}.pdf"}
    )