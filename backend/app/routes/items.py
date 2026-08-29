from fastapi import APIRouter
from app.services.zoho.modules.items import get_items, get_item

router = APIRouter()

@router.get("/items")
async def items():
    return await get_items()

@router.get("/items/{item_id}")
async def item_detail(item_id: str):
    return await get_item(item_id)