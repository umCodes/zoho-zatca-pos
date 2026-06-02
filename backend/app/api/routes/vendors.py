from fastapi import APIRouter
from app.models.vendors_models import VendorModel
from app.controllers.vendors_controllers import create_vendor

router = APIRouter()

@router.post("/vendors")
async def vendor(expense_data: VendorModel):
    return await create_vendor(expense_data)