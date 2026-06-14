from app.services.zoho.models.expenses_models import CreateExpenseZoho

from app.database.schemas import ExpenseCreate
from app.database.services import create_expense_db

from app.database.setup import get_db
from app.services.orchestrators.contact_services import resolve_vendor
from app.services.zoho.modules.expenses import create_expense_in_zoho
from app.database.models import Expense

import json
# Saves Expense to Database
def save_expense_to_db(db, expense: dict):
    print("- Saving Expense to Database...")
    return create_expense_db(
        db=db,
        expense=ExpenseCreate(
            expense_id=expense.get("expense_id", ""),
            tax_reg_no=expense.get("tax_reg_no", ""),
            amount=expense.get("amount", ""),
            reference_number=expense.get("reference_number", ""),
            date=expense.get("date", ""),
            vendor_id=expense.get("vendor_id", "")
        )
    )
    
async def create_expense(expense: CreateExpenseZoho):
    print("- Creating Expense...")
    # Intiate database connection
    db = next(get_db())

    # Create or Find Vendor
    vendor = await resolve_vendor(db, expense)
    print("vendor: ", json.dumps(vendor, indent=2))
    if not vendor["ok"]:
        return vendor

    # Create Expense in Zoho with vendor id
    zoho_expense = await create_expense_in_zoho(expense, vendor["contact_id"])
    if not zoho_expense["ok"]:
        return zoho_expense

    # Save Expense to Database
    saved = save_expense_to_db(db, zoho_expense["expense"])
    if not isinstance(saved, Expense):
        return saved

    return {
        "ok": True,
        "expense": zoho_expense["expense"]
    }