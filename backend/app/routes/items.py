from fastapi import APIRouter
from app.services.zoho.modules.items import get_items

router = APIRouter()

@router.get("/items")
async def items():
    return await get_items()