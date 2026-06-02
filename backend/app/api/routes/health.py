from fastapi import APIRouter
from app.services.gemini_services import process_img
router = APIRouter()

@router.get("/health")
async def health_check():
    print("Hello")
    return {
        "status": "ok",
        "service": "running"
    }