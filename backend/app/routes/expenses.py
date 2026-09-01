import base64
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database.schemas import ExpenseResponse
from app.database.services import list_expenses_db
from app.database.setup import get_db
from app.services.gemini_services import process_img
from app.services.orchestrators.expenses_services import create_expense, delete_expense
from app.services.zoho.models.expenses_models import CreateExpenseZoho
from app.utils.qr_decoder import decode_qr_code

router = APIRouter()


@router.get("/expenses", response_model=list[ExpenseResponse])
async def list_expenses(db: Session = Depends(get_db)):
    """Lists recorded purchase invoices from the local Postgres mirror
    (vendor pre-joined in one query) — avoids hitting Zoho's API just to
    render a list view."""
    return list_expenses_db(db=db)


@router.post("/upload")
async def upload_purchase_invoice(file: UploadFile = File(...)):
    """Extracts purchase-invoice fields from an uploaded photo — tries the
    ZATCA QR code first (fast, no AI cost), and falls back to a full Gemini
    vision scan of the receipt when no QR code is found. Meant to pre-fill
    the expense confirmation form, mirroring the Telegram bot's /qrcode and
    /full_ai_scan commands."""
    contents = await file.read()

    qr_data = decode_qr_code(contents).get("data")
    if qr_data:
        return {"ok": True, "source": "qr", "data": qr_data}

    b64_data = base64.b64encode(contents).decode("utf-8")
    try:
        data = await process_img(b64_data)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Invoice scan failed: {e}")

    if "contact_name" not in data:
        raise HTTPException(status_code=422, detail="Could not extract invoice data from image")

    return {"ok": True, "source": "ai", "data": data}


@router.post("/expenses")
async def submit_expense(expense: CreateExpenseZoho):
    """Creates the (user-confirmed/edited) purchase invoice as a Zoho expense —
    resolving or creating the vendor, then mirroring the expense into Postgres."""
    result = await create_expense(expense=expense)
    if not result.get("ok"):
        raise HTTPException(status_code=409, detail=result)
    return result


@router.delete("/expenses/{expense_id}")
async def remove_expense(expense_id: str):
    """Deletes a purchase invoice — removes it from Zoho Books first, then
    from the local Postgres mirror. Used to undo an accidental or duplicate
    submission."""
    result = await delete_expense(expense_id=expense_id)
    if not result.get("ok"):
        status_code = 404 if result.get("error") == "Expense not found" else 409
        raise HTTPException(status_code=status_code, detail=result)
    return result
