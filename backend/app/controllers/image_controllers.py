from fastapi import UploadFile, File
import httpx
from app.services.gemini_services import process_img
import base64
# from app.services.qr_services import read_qr_code 
from app.utils.qr_decoder import decode_qr_code



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
    

async def upload_qr_image(file: UploadFile = File(...), image_bytes: bytes = None, image_base64: str = None):
    try:
        
        if not file and not image_bytes and not image_base64:
            raise ValueError("No file uploaded")
        if file and file.content_type not in ["image/png", "image/jpeg"]:
            raise ValueError("Unsupported file type. Please upload a PNG or JPEG image.")


        if image_bytes: 
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        if image_base64:
            data = decode_qr_code(image_base64)
            return data
        
        if file and file.content_type in ["image/png", "image/jpeg"]:
            image_bytes = await file.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            data = decode_qr_code(image_base64)
            return data
        
    except ValueError as e:
        print(f"{e}")
        return {
            "error": str(e)
        }
    except Exception as e:
        return {
            "error": "Unexpected error processing QR code"
        }
    