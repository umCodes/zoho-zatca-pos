from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    print("hey")
    return {
        "status": "ok",
        "service": "running"
    }