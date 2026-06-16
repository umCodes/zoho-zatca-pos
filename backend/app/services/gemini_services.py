import httpx
from app.utils.images import encode_image_to_base64
from app.utils.json import parse_json_response
from app.core.config import GEMINI_API_KEY

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


async def process_img(img: str):
    # base64_img = encode_image_to_base64(img_url) 
    res = await Gemini(PROMPT, img)
    return parse_json_response(res)


async def Gemini(prompt: str, img: str = None):
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
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
    body = { "contents": [{ "parts": parts }] }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(URL,headers=headers,json=(body))
            data = res.json()
            print(data)
            if "candidates" not in data:
                raise ValueError(f"Gemini API error: {data['candidates'][0].get('output', {}).get('content', 'No content in response')}")
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except httpx.HTTPStatusError as e:
        print(f"HTTP error from Gemini API: {e.response.status_code} - {e.response.text}")
        return e
    except ValueError as e:
        print(f"{e}")
        return e
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return e
