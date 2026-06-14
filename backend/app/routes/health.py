from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    print("Hello")
    return {
        "status": "ok",
        "service": "running"
    }