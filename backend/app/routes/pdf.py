from fastapi import APIRouter
from app.controllers.pdf_controllers import get_pdf

router = APIRouter()

@router.get("/invoice/{invoice_id}/pdf")
async def get_invoice_pdf(invoice_id: str):
    return await get_pdf(invoice_id)