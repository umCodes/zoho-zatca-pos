from fastapi import APIRouter, Query
from app.controllers.fatoora_controllers import _push_invoices

router = APIRouter()

@router.get("/push-invoices")
async def push_invoices(
    from_date: str = Query(..., alias="from", description="Start date in ISO format (YYYY-MM-DD)"),
    to_date: str = Query(default=None, alias="to", description="End date in ISO format (YYYY-MM-DD)"),
):
    result = await _push_invoices(from_date)
    return {"success": True, **result}
