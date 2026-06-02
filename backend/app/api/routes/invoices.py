from fastapi import APIRouter
from app.models.invoice_models import LineItem
from app.services.invoice_service import create_walk_in_invoice

router = APIRouter()

@router.post("/invoices/walk-in")
async def walk_in(line_items: list[LineItem], method: str = "Cash"):
    return await create_walk_in_invoice(line_items, method)