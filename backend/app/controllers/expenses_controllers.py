# services/expenses.py
from app.models.expenses_models import ExpenseModel
from app.services.zoho_client import zoho_post
from app.utils.filters import filter_fields


async def create_purchase(expense_data: ExpenseModel) -> dict:
    payload = {
        "account_id": expense_data.account_id,
        "date": expense_data.date,
        "amount": float(expense_data.amount),
        "paid_through_account_id": expense_data.paid_through_account_id,
        "reference_number": expense_data.reference_number,
        "tax_id": expense_data.tax_id,
        "tax_treatment": expense_data.tax_treatment,
        "place_of_supply": expense_data.place_of_supply,
        "is_inclusive_tax": expense_data.is_inclusive_tax,
    }

    if expense_data.tax_treatment == "vat_registered":
        payload["tax_reg_no"] = expense_data.tax_reg_no
        payload["tax_percentage"] = expense_data.tax_percentage

    if expense_data.vendor_id:
        payload["vendor_id"] = expense_data.vendor_id

    res = await zoho_post("/expenses", payload)
    data = res.json()
    print(data)
    if "expense" not in data:
        raise ValueError(f"Failed to create expense: {data.get('message', 'Unknown error')}")
    fields_to_keep = [
    "expense_id",
    "transaction_type",
    "account_id",
    "tax_reg_no",
    "tax_treatment",
    "vendor_id",
    "vendor_name",
    "date",
]

    filtered = filter_fields(data["expense"], fields_to_keep)
    return data["expense"]