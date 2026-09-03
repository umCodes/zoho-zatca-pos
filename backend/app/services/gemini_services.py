import httpx
from app.utils.images import encode_image_to_base64
from app.utils.json import parse_json_response
from app.core.config import GEMINI_API_KEY, GEMINI_API_KEY_2

MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

REQUEST_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


class ScanOverloadedError(Exception):
    """Gemini is rate-limiting or out of quota on every configured key."""


class ScanTimeoutError(Exception):
    """Gemini did not respond within REQUEST_TIMEOUT."""

PROMPT = """
    Extract invoice data. Return valid JSON only — no explanations.
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
"""

# Errors that should trigger a fallback to the next key
QUOTA_ERROR_CODES = {429, 403}


async def process_img(img: str):
    res = await Gemini_with_fallback(PROMPT, img)
    if isinstance(res, Exception):
        raise res
    return parse_json_response(res)


# Gemini's inline_data accepts these directly — anything else falls back to
# image/jpeg, which matches how QR/receipt photos are already sent from the
# Telegram bot (always JPEG-encoded before reaching this service).
SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}


CUSTOMER_DOCUMENT_PROMPT = """
    Extract customer/business registration details from this document
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
"""


async def process_customer_document(img: str, mime_type: str = "image/jpeg"):
    res = await Gemini_with_fallback(CUSTOMER_DOCUMENT_PROMPT, img, mime_type=mime_type)
    if isinstance(res, Exception):
        return res
    return parse_json_response(res)


async def Gemini_with_fallback(prompt: str, img: str = None, mime_type: str = "image/jpeg"):
    """Try each API key in order, falling back on quota/auth errors."""
    api_keys = [key for key in [GEMINI_API_KEY, GEMINI_API_KEY_2] if key]

    last_error = None
    all_quota_errors = True
    for i, key in enumerate(api_keys):
        try:
            result = await Gemini(prompt, img, api_key=key, mime_type=mime_type)
            if isinstance(result, Exception):
                raise result
            return result
        except Exception as e:
            last_error = e
            if not isinstance(e, httpx.HTTPStatusError) or e.response.status_code not in QUOTA_ERROR_CODES:
                all_quota_errors = False
            is_last = i == len(api_keys) - 1
            if not is_last:
                print(f"Key {i + 1} failed ({e}), trying next key...")
            else:
                print(f"All API keys exhausted. Last error: {e}")

    if last_error is None:
        return None
    if isinstance(last_error, (httpx.TimeoutException, ScanTimeoutError)):
        return ScanTimeoutError("Invoice scan timed out")
    if all_quota_errors:
        return ScanOverloadedError("Invoice scan service is out of capacity")
    return last_error


async def Gemini(prompt: str, img: str = None, api_key: str = None, mime_type: str = "image/jpeg"):
    key = api_key or GEMINI_API_KEY
    headers = {
        "x-goog-api-key": key,
        "Content-Type": "application/json"
    }
    parts = []

    if img:
        parts.append({
            "inline_data": {
                "mime_type": mime_type if mime_type in SUPPORTED_MIME_TYPES else "image/jpeg",
                "data": img
            }
        })
    parts.append({"text": prompt})
    body = {"contents": [{"parts": parts}]}

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            res = await client.post(URL, headers=headers, json=body)

            # Raise immediately on quota/auth errors so fallback can catch them
            if res.status_code in QUOTA_ERROR_CODES:
                res.raise_for_status()

            data = res.json()
            print(data)

            if "candidates" not in data:
                raise ValueError(f"Gemini API error: no candidates in response")

            return data["candidates"][0]["content"]["parts"][0]["text"]

    except httpx.TimeoutException as e:
        print(f"Timeout calling Gemini API: {e}")
        raise ScanTimeoutError("Invoice scan timed out") from e
    except httpx.HTTPStatusError as e:
        print(f"HTTP error from Gemini API: {e.response.status_code} - {e.response.text}")
        raise  # Re-raise so fallback wrapper catches it
    except ValueError as e:
        print(f"{e}")
        raise
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise
