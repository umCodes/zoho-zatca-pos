from fastapi import UploadFile, File
import httpx
from app.services.gemini_services import process_img
import base64



async def upload_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        data = await process_img(image_base64)
        return {
            "data": data
        }     
    except httpx.HTTPException as e:
        return {
            "error": e.detail
        }
    except ValueError as e:
        print(f"{e}")
        return e
    except Exception as e:
        return {
            "error": str(e)
        }
    