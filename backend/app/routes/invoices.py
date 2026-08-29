from fastapi import APIRouter
from app.services.zoho.models.invoices_models import LineItem
from app.services.zoho.modules.invoices import (
    create_walk_in_invoice,
    create_b2b_invoice,
    create_b2b_invoice_confirmed,
    mark_invoice_as_sent,
    get_todays_invoices,
)

router = APIRouter()

@router.get("/invoices/today")
async def todays_invoices():
    return await get_todays_invoices()

@router.post("/invoices/walk-in")
async def walk_in(line_items: list[LineItem], method: str = "Cash"):
    return await create_walk_in_invoice(line_items, method)

@router.post("/invoices/b2b")
async def b2b(customer_id: str, line_items: list[LineItem]):
    return await create_b2b_invoice(customer_id, line_items)

@router.post("/invoices/b2b/confirm")
async def b2b_confirm(customer_id: str, line_items: list[LineItem]):
    return await create_b2b_invoice_confirmed(customer_id, line_items)

@router.post("/invoices/{invoice_id}/send")
async def send_invoice(invoice_id: str):
    message = await mark_invoice_as_sent(invoice_id)
    return {"ok": True, "message": message}