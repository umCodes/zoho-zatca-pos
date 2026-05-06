from fastapi import APIRouter
from app.services.item_service import get_items

router = APIRouter()

@router.get("/items")
async def items():
    return await get_items()