from httpx import HTTPStatusError
from app.services.zoho.client import zoho_client
from app.services.zoho.models.expenses_models import CreateExpenseZoho
from app.utils.filters import filter_list_fields, filter_fields
import json

async def get_expenses():
    try:
        response = await zoho_client.request(path="/expenses",include_org_id=True)
        data = response.json()

        if data.get("message") != "success":
            return { "ok": False, "error": data }

        return {
            "ok": True,
            "expenses": filter_list_fields(
                data=data["expenses"], 
                fields_to_keep=[
                    "expense_id",
                    "tax_reg_no",
                    "total",
                    "reference_number",
                    "date",
                    "vendor_id"
                ])
        }
    except HTTPStatusError as e:
        print(e)
        return {
            "ok": False,
            "error": e
        }

async def get_expense(id: str):
    try:
        response = await zoho_client.request(path=f"/expenses/{id}",include_org_id=True)
        data = response.json()


        if data.get("message") != "success":
            return { "ok": False, "error": data }

        return {
            "ok": True,
            "expense": filter_fields(
                data=data["expense"], 
                fields_to_keep=[
                    "expense_id",
                    "tax_reg_no",
                    "amount",
                    "reference_number",
                    "date",
                    "vendor_id"
                ])
        }
    except HTTPStatusError as e:
        print(e)
        return {
            "ok": False,
            "error": e
        }


# async def create_expense(expense: CreateExpenseZoho):
#     # print(expense.model_dump())
#     try:
#         db = next(get_db())
#         vendor = get_contact_by_tax_reg_no_db(db=db, tax_reg_no=expense.tax_reg_no)
#         if not vendor and not expense.contact_name:
#             return {
#                 "ok": False,
#                 "from": "db",
#                 "message": "Vendor doesn't exist. Please provide a valid vendor name to create a vendor with your expense."
#             }
        
#         vendor = await create_contact(CreateContactZoho(
#             contact_type="vendor",
#             contact_name=expense.contact_name,
#             tax_reg_no=expense.tax_reg_no,
#             tax_treatment="vat_registered" if expense.tax_reg_no else "vat_not_registered",
#         ))
#         if vendor["ok"] == False:
#             return vendor
#         create_contact_db(db,contact=ContactCreate(**vendor))
#         expense.vendor_id = vendor.contact_id
#         response = await zoho_client.request(
#             method="POST",
#             path="/expenses",
#             json=expense.model_dump(),
#             include_org_id=True
#         )
#         data = response.json()

#         if data.get("code") != 0 or not data.get("expense"):
#             return { "ok": False, "error": data }
#         filtered = filter_fields(
#                 data=data["expense"], 
#                 fields_to_keep=[
#                     "expense_id",
#                     "tax_reg_no",
#                     "amount",
#                     "reference_number",
#                     "date",
#                     "vendor_id"
#                 ])

#         create_expense_db(db=db, expense=ExpenseCreate(
#             expense_id=filtered.get("expense_id", ""),
#             tax_reg_no=filtered.get("tax_reg_no", ""),
#             amount=filtered.get("amount", ""),
#             reference_number=filtered.get("reference_number", ""),
#             date=filtered.get("date", ""),
#             vendor_id=filtered.get("vendor_id", "")
#         ))
#         return {
#             "ok": True,
#             "expense": filtered
#         }
#     except HTTPStatusError as e:
#         print(e)
#         return {
#             "ok": False,
#             "error": e
#         }


async def is_expense_exists(expense: CreateExpenseZoho):
    print("- Checking if Expense exists in Zoho...")
    print("   * reference_number_contains: ", expense.reference_number)
    try:
        zoho_expense = await zoho_client.request(
            path="/expenses",
            include_org_id=True,
            params={
                "reference_number_contains": expense.reference_number,
            }
        )

        zoho_expense = zoho_expense.json()
        if zoho_expense.get("expenses") or len(zoho_expense.get("expenses")) > 0:
            return {
                "ok": True,
                "expense": zoho_expense.get("expenses")[0]
            }
        else:
            return False
    except Exception as e:
        print("Is Expense Exists Error: ", e)
        return {
            "ok": False,
            "error": e
        }
        

async def create_expense_in_zoho(expense: CreateExpenseZoho, vendor_id: str):
    print("- Creating Expense in Zoho...")
    expense.vendor_id = vendor_id

    expense.reference_number = expense.reference_number.lower()
    expense.description = json.dumps(expense.description)

    is_exists = await is_expense_exists(expense)
    if is_exists:
        return {
            "ok": False,
            "error": "Expense already exists"
        }
    
    response = await zoho_client.request(
        method="POST",
        path="/expenses",
        json=expense.model_dump(),
        include_org_id=True
    )

    data = response.json()

    if data.get("code") != 0 or not data.get("expense"):
        return {"ok": False, "error": data}

    filtered = filter_fields(
        data=data["expense"],
        fields_to_keep=[
            "expense_id",
            "tax_reg_no",
            "amount",
            "reference_number",
            "date",
            "vendor_id"
        ]
    )

    return {"ok": True, "expense": filtered}

