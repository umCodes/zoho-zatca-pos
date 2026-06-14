import os
import json
import httpx
from dotenv import load_dotenv
from app.core.config import OPEN_ROUTER_KEY

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-120b:free"

async def open_router(prompt: str, model: str = MODEL) -> str:
    headers = {
        "Authorization": f"Bearer {OPEN_ROUTER_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(BASE_URL, headers=headers, json=body)
            data = res.json()

            if not res.is_success:
                raise ValueError(f"HTTP error: {res.status_code} - {data}")

            return data["choices"][0]["message"]["content"]

    except httpx.HTTPStatusError as e:
        print(f"HTTP error from OpenRouter API: {e.response.status_code} - {e.response.text}")
        return e
    except (KeyError, IndexError) as e:
        print(f"Unexpected response structure: {e}")
        return e
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return e


def build_prompt(item: dict) -> str:
    return f"""
    You will receive a JSON object representing a Zoho Books item. Your task is to normalize the item's data to conform to the model below.
    **Transformation rules:**
    - **name** – Set to the item's Arabic name. If missing, generate an appropriate Arabic name based on the available item data.
    - **name_sec_lang** – Set to the item's English name. If missing, generate an appropriate English name based on the available item data.
    - **sku** – Include only if present; leave as "" otherwise.
    - **unit** – Keep as-is.
    - **description** – Format as: "English Name + Arabic Name". If either name is missing, use a generated name in its place.
    - **rate** – Keep as-is.
    - **tax_id** – Always set to "46324000000043661".
    - **tax_name** – Always set to "Standard Rate".
    - **tax_percentage** – Always set to 15.
    - **tax_type** – Always set to "tax".
    - **tax_status** – Always set to "Active".
    - **tax_country_code** – Always set to "SA".
    - **is_taxable** – Always set to true.
    **Return only the corrected JSON object with no additional explanation.**
    When translating from English to Arabic:
    • Do NOT fully translate proper nouns, brand names, or uncommon names
    • Transliterate brand names and proper nouns in English letters (romanization)
    • Only translate common words (e.g., "coffee", "tea", "spice", etc)
    • Format: [Common word translation] + [Transliterate proper noun]
    Note: Some items may be of Ethiopian origin and may have inconsistent naming. Use the most standard spelling of the Ethiopian name in both Arabic and English, ignoring incorrect variants.
    All items belong to one of these categories:
    "Spice", "Herbs", "Incenses", "Perfumes", "Cosmetics", "Coffee", "Legumes".
    Ensure the generated name clearly fits one of these categories.
    Here is the item:
    {json.dumps(item, indent=2, ensure_ascii=False)}
"""


async def process_item(item: dict) -> dict:
    response = await open_router(build_prompt(item))
    return json.loads(response)