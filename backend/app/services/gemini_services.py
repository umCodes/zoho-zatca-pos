import httpx
from app.utils.images import encode_image_to_base64
from app.utils.json import parse_json_response
from app.core.config import GEMINI_API_KEY, GEMINI_API_KEY_2

MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

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
    return parse_json_response(res)


async def Gemini_with_fallback(prompt: str, img: str = None):
    """Try each API key in order, falling back on quota/auth errors."""
    api_keys = [key for key in [GEMINI_API_KEY, GEMINI_API_KEY_2] if key]

    last_error = None
    for i, key in enumerate(api_keys):
        try:
            result = await Gemini(prompt, img, api_key=key)
            if isinstance(result, Exception):
                raise result
            return result
        except Exception as e:
            last_error = e
            is_last = i == len(api_keys) - 1
            if not is_last:
                print(f"Key {i + 1} failed ({e}), trying next key...")
            else:
                print(f"All API keys exhausted. Last error: {e}")

    return last_error


async def Gemini(prompt: str, img: str = None, api_key: str = None):
    key = api_key or GEMINI_API_KEY
    headers = {
        "x-goog-api-key": key,
        "Content-Type": "application/json"
    }
    parts = []

    if img:
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": img
            }
        })
    parts.append({"text": prompt})
    body = {"contents": [{"parts": parts}]}

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(URL, headers=headers, json=body)

            # Raise immediately on quota/auth errors so fallback can catch them
            if res.status_code in QUOTA_ERROR_CODES:
                res.raise_for_status()

            data = res.json()
            print(data)

            if "candidates" not in data:
                raise ValueError(f"Gemini API error: no candidates in response")

            return data["candidates"][0]["content"]["parts"][0]["text"]

    except httpx.HTTPStatusError as e:
        print(f"HTTP error from Gemini API: {e.response.status_code} - {e.response.text}")
        raise  # Re-raise so fallback wrapper catches it
    except ValueError as e:
        print(f"{e}")
        raise
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise
