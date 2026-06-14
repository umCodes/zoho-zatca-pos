from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import PASSWORD





router = APIRouter()

class CheckRequest(BaseModel):
    value: str


@router.post("/check_password")
def check_value(body: CheckRequest):
    return {
        "match": body.value == (PASSWORD)
    }