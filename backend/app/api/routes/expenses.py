from fastapi import APIRouter
from app.models.expenses_models import ExpenseModel
from app.controllers.expenses_controllers import create_purchase

router = APIRouter()

@router.post("/expenses")
async def purchase(expense_data: ExpenseModel):
    return await create_purchase(expense_data)