import json
import base64
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.schemas import ExpenseResponse
from app.database.services import list_expenses_db
from app.database.setup import get_db
from app.services.mistral_services import ScanOverloadedError, ScanTimeoutError, process_img
from app.services.orchestrators.batch_capture_services import scan_and_record_expense
from app.services.orchestrators.expenses_services import create_expense, delete_expense, delete_expenses
from app.services.zoho.models.expenses_models import CreateExpenseZoho
from app.utils.qr_decoder import decode_qr_code

router = APIRouter()

# Holds receipt image bytes between POST /upload (extraction) and POST
# /expenses (creation), keyed by upload_id — the two are separate requests
# once the user has reviewed/edited the extracted fields in between.
_pending_receipts: dict[str, tuple[bytes, str, str]] = {}
# Receipts whose scan is never confirmed would otherwise pile up in RAM
# forever; keep only the most recent ones (dicts preserve insertion order).
_MAX_PENDING_RECEIPTS = 10

# The admin app shrinks images before sending (~0.2–0.5 MB), so anything
# far larger is refused rather than held in a 512 MB server's memory.
MAX_SCAN_UPLOAD_BYTES = 8 * 1024 * 1024


def _remember_receipt(upload_id: str, receipt: tuple[bytes, str, str]) -> None:
    _pending_receipts[upload_id] = receipt
    while len(_pending_receipts) > _MAX_PENDING_RECEIPTS:
        _pending_receipts.pop(next(iter(_pending_receipts)))


class DeleteExpensesRequest(BaseModel):
    expense_ids: list[str]


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
    upload_id = uuid.uuid4().hex
    _remember_receipt(upload_id, (contents, file.filename or "receipt.jpg", file.content_type or "image/jpeg"))

    qr_data = decode_qr_code(contents).get("data")
    if qr_data:
        return {"ok": True, "source": "qr", "data": qr_data, "upload_id": upload_id}

    b64_data = base64.b64encode(contents).decode("utf-8")
    try:
        data = await process_img(b64_data)
    except ScanOverloadedError as e:
        raise HTTPException(
            status_code=503,
            detail={"ok": False, "error": {"code": "overloaded", "message": str(e)}},
        )
    except ScanTimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail={"ok": False, "error": {"code": "timeout", "message": str(e)}},
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail={"ok": False, "error": {"code": "generic", "message": f"Invoice scan failed: {e}"}},
        )

    if "contact_name" not in data:
        raise HTTPException(
            status_code=422,
            detail={"ok": False, "error": {"code": "no_data", "message": "Could not extract invoice data from image"}},
        )

    return {"ok": True, "source": "ai", "data": data, "upload_id": upload_id}


@router.post("/expenses/auto")
async def scan_and_record(
    file: UploadFile = File(...),
    fields: str | None = Form(None),
):
    """Scans one invoice image and records it in a single step — used by
    the admin app's multi-image upload, which sends images one at a time.

    Always answers 200 with a per-image outcome rather than an HTTP error,
    so one bad image never stops the rest of the batch:
      {"status": "recorded" | "duplicate" | "failed", "source", "data",
       "expense"?, "error"?: {"code", "message"}}

    QR codes are not read here (the ZATCA QR has no invoice number, so the
    AI scan reads every field). Optional `fields` (JSON) are user-corrected
    invoice fields for an image that failed before — they are recorded
    as-is, with no scan."""
    try:
        parsed_fields = json.loads(fields) if fields else None
    except ValueError:
        parsed_fields = None
    if parsed_fields is not None and not isinstance(parsed_fields, dict):
        parsed_fields = None
    contents = await file.read(MAX_SCAN_UPLOAD_BYTES + 1)
    await file.close()
    if len(contents) > MAX_SCAN_UPLOAD_BYTES:
        return {
            "status": "failed", "source": None, "data": {},
            "error": {"code": "too_large", "message": "Image is too large (max 8 MB)."},
        }
    if not contents:
        return {
            "status": "failed", "source": None, "data": {},
            "error": {"code": "empty", "message": "The image was empty."},
        }
    return await scan_and_record_expense(
        contents=contents,
        filename=file.filename or "receipt.jpg",
        content_type=file.content_type or "image/jpeg",
        fields=parsed_fields,
    )


@router.post("/expenses")
async def submit_expense(expense: CreateExpenseZoho):
    """Creates the (user-confirmed/edited) purchase invoice as a Zoho expense —
    resolving or creating the vendor, then mirroring the expense into Postgres.
    If `upload_id` matches a receipt from a prior POST /upload, that image is
    attached to the created expense in Zoho."""
    image = _pending_receipts.pop(expense.upload_id, None) if expense.upload_id else None
    result = await create_expense(
        expense=expense,
        image_bytes=image[0] if image else None,
        image_filename=image[1] if image else None,
        image_content_type=image[2] if image else None,
    )
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


@router.delete("/expenses")
async def remove_expenses(body: DeleteExpensesRequest):
    """Deletes several purchase invoices at once — the Zoho-side deletes run
    concurrently, and only the ones that succeeded there are removed from
    Postgres, in a single statement. Used for multi-select delete in the UI."""
    if not body.expense_ids:
        raise HTTPException(status_code=422, detail="expense_ids must not be empty")
    result = await delete_expenses(expense_ids=body.expense_ids)
    if not result.get("ok"):
        raise HTTPException(status_code=409, detail=result)
    return result
