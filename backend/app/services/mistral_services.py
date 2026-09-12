import httpx
from app.utils.json import parse_json_response
from app.core.config import MISTRAL_API_KEY
from app.services.openrouter_services import open_router

OCR_MODEL = "mistral-ocr-latest"
OCR_URL = "https://api.mistral.ai/v1/ocr"

REQUEST_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


class ScanOverloadedError(Exception):
    """Mistral is rate-limiting or out of quota."""


class ScanTimeoutError(Exception):
    """Mistral did not respond within REQUEST_TIMEOUT."""


# Mistral's OCR endpoint only accepts image_url/document_url inputs — PDFs
# and images both go through "document_url", the distinction is the data URI's
# declared mime type.
SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}

QUOTA_ERROR_CODES = {429, 403}

PROMPT = """
    Extract invoice data from the OCR text below. Return valid JSON only — no explanations.
    Rules:
    - Preserve original language; include ar/en when both exist
    - Dates: YYYY-MM-DDTHH:mm:ss
    - Numbers (not strings) for numeric fields
    - "" for missing values; omit nothing
    - if an English translation is not provided, create one. Transliterate the brand or company name, and translate the other terms.

    {
        "date": "",<- YYYY-MM-DD only no time included
        "amount": 0, <- tax-inclusive
        "reference_number": "", <- invoice number
        "tax_treatment": "vat_registered | vat_not_registered", <- if VAT No is present, it's vat_registered; otherwise vat_not_registered
        "tax_reg_no": "",<- vat registration number,
        "contact_name": "" <- the name of the vendor (arabic name if available, otherwise transliterate the english name)
  }

    OCR text:
    {ocr_text}
"""

CUSTOMER_DOCUMENT_PROMPT = """
    Extract customer/business registration details from the OCR text below
    (e.g. a Commercial Registration certificate, National Address certificate,
    or VAT certificate). Return valid JSON only — no explanations.
    Rules:
    - Preserve original language; fill both ar/en variants when both exist
    - If a field's English value is missing but the Arabic is present, transliterate
      the name/street/district into English rather than leaving it empty
    - Numbers as plain digit strings (not localized digits), "" for missing values
    - omit nothing — always return every key below

    {
        "contact_name": "", <- primary business/establishment name, Arabic
        "contact_name_sec_lang": "", <- same name in English
        "phone": "",
        "tax_reg_no": "", <- VAT / TRN number (15 digits in Saudi Arabia)
        "buyer_id_label": "", <- one of: CRN, TIN, NAT, IQA, PAS, MOM, MLS, SAG, GCC, OTH, 700 — "CRN" if this is a Commercial Registration document
        "buyer_id_value": "", <- the ID number matching buyer_id_label (e.g. the CR number)
        "billing_address": {
            "building_number": "", <- 4-digit building number, Arabic/local form
            "building_number_sec_lang": "",
            "street": "",
            "street_sec_lang": "",
            "additional_number": "", <- 4-digit additional number (Saudi National Address)
            "additional_number_sec_lang": "",
            "district": "",
            "district_sec_lang": "",
            "city": "",
            "city_sec_lang": "",
            "state": "", <- region/province
            "state_sec_lang": "",
            "zip": "", <- 5-digit postal code
            "zip_sec_lang": "",
            "country": "",
            "country_sec_lang": ""
        }
    }

    OCR text:
    {ocr_text}
"""


async def process_img(img: str, mime_type: str = "image/jpeg"):
    ocr_text = await run_ocr(img, mime_type=mime_type)
    if isinstance(ocr_text, Exception):
        raise ocr_text
    res = await open_router(PROMPT.replace("{ocr_text}", ocr_text))
    if isinstance(res, Exception):
        raise res
    return parse_json_response(res)


async def process_customer_document(img: str, mime_type: str = "image/jpeg"):
    ocr_text = await run_ocr(img, mime_type=mime_type)
    if isinstance(ocr_text, Exception):
        return ocr_text
    res = await open_router(CUSTOMER_DOCUMENT_PROMPT.replace("{ocr_text}", ocr_text))
    if isinstance(res, Exception):
        return res
    return parse_json_response(res)


async def run_ocr(img: str, mime_type: str = "image/jpeg"):
    mime = mime_type if mime_type in SUPPORTED_MIME_TYPES else "image/jpeg"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }
    data_uri = f"data:{mime};base64,{img}"
    document = (
        {"type": "document_url", "document_url": data_uri}
        if mime == "application/pdf"
        else {"type": "image_url", "image_url": data_uri}
    )
    body = {
        "model": OCR_MODEL,
        "document": document,
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            res = await client.post(OCR_URL, headers=headers, json=body)
            print(f"Mistral OCR response [{res.status_code}]: {res.text[:500]}")

            if res.status_code in QUOTA_ERROR_CODES:
                return ScanOverloadedError("Invoice scan service is out of capacity")

            res.raise_for_status()
            data = res.json()

            pages = data.get("pages", [])
            if not pages:
                raise ValueError("Mistral OCR error: no pages in response")

            return "\n\n".join(page.get("markdown", "") for page in pages)

    except httpx.TimeoutException as e:
        print(f"Timeout calling Mistral OCR API: {e}")
        return ScanTimeoutError("Invoice scan timed out")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error from Mistral OCR API: {e.response.status_code} - {e.response.text}")
        return e
    except Exception as e:
        print(f"Error calling Mistral OCR API: {e}")
        return e
