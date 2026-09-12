import base64
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.zoho.models.contacts_models import CreateCustomerDetailedZoho
from app.services.zoho.modules.contacts import get_customers, get_customer, create_customer_detailed_in_zoho
from app.services.mistral_services import process_customer_document
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

@router.post("/customers/scan")
async def scan_customer_document(file: UploadFile = File(...)):
    """Extracts customer/address fields from an uploaded document — a photo
    (CR certificate, National Address certificate, VAT certificate, etc.) or
    a PDF — using Gemini vision. Meant to pre-fill the create-customer form."""
    contents = await file.read()
    b64_data = base64.b64encode(contents).decode("utf-8")
    mime_type = file.content_type or "image/jpeg"

    result = await process_customer_document(b64_data, mime_type=mime_type)

    if isinstance(result, Exception):
        raise HTTPException(status_code=502, detail=f"Document scan failed: {result}")

    return {"ok": True, "data": result}

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
