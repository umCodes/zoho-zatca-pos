from fastapi import APIRouter, UploadFile
from app.controllers.image_controllers import upload_image

router = APIRouter()

@router.post("/upload")
async def process_image(file: UploadFile):
    return await upload_image(file)