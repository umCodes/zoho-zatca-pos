import base64
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.zoho.models.contacts_models import CreateCustomerDetailedZoho
from app.services.zoho.modules.contacts import get_customers, get_customer, create_customer_detailed_in_zoho
from app.services.mistral_services import process_customer_documents
from app.services.openrouter_services import translate_address_field

router = APIRouter()


class TranslateFieldRequest(BaseModel):
    field: str
    value: str

@router.get("/customers")
async def customers(search: str = ""):
    return await get_customers(search)

@router.post("/customers")
async def create_customer(customer: CreateCustomerDetailedZoho):
    return await create_customer_detailed_in_zoho(customer)

@router.get("/customers/{customer_id}")
async def customer(customer_id: str):
    return await get_customer(customer_id)

# Limits for a multi-document scan. The frontend compresses photos before
# upload (~200-500 KB each), so these only bite on uncompressed PDFs or
# misbehaving clients — they keep a single request from exhausting the
# small Render instance's memory.
MAX_SCAN_FILES = 10
MAX_SCAN_FILE_BYTES = 8 * 1024 * 1024
MAX_SCAN_TOTAL_BYTES = 25 * 1024 * 1024


@router.post("/customers/scan")
async def scan_customer_document(
    files: list[UploadFile] = File(default=[]),
    file: UploadFile | None = File(default=None),
):
    """Extracts customer/address fields from one or more uploaded documents —
    photos (CR certificate, National Address certificate, VAT certificate,
    etc.) and/or PDFs — merged into a single result. Meant to pre-fill the
    create-customer form. Accepts `files` (multiple) or the legacy single
    `file` field."""
    uploads = list(files)
    if file is not None:
        uploads.append(file)
    if not uploads:
        raise HTTPException(status_code=422, detail="No files uploaded")
    if len(uploads) > MAX_SCAN_FILES:
        raise HTTPException(status_code=413, detail=f"Too many files (max {MAX_SCAN_FILES})")

    docs: list[tuple[str, str]] = []
    total = 0
    for up in uploads:
        contents = await up.read()
        await up.close()
        if len(contents) > MAX_SCAN_FILE_BYTES:
            raise HTTPException(status_code=413, detail=f"'{up.filename}' is too large")
        total += len(contents)
        if total > MAX_SCAN_TOTAL_BYTES:
            raise HTTPException(status_code=413, detail="Upload too large in total")
        docs.append((base64.b64encode(contents).decode("utf-8"), up.content_type or "image/jpeg"))
        del contents

    result, failed = await process_customer_documents(docs)

    if isinstance(result, Exception):
        raise HTTPException(status_code=502, detail=f"Document scan failed: {result}")

    return {"ok": True, "data": result, "scanned": len(docs) - len(failed), "failed": failed}

@router.post("/customers/translate-field")
async def translate_field(body: TranslateFieldRequest):
    """Translates a single Arabic address field to English — used to
    auto-fill the secondary-language address inputs as the user types."""
    if not body.value.strip():
        return {"ok": True, "value": ""}
    try:
        translated = await translate_address_field(body.field, body.value)
        return {"ok": True, "value": translated}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Translation failed: {e}")
