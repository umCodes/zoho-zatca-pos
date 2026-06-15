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




async def is_expense_exists(expense: CreateExpenseZoho):

    print("- Checking if Expense exists in Zoho (by reference_number)...")

    print("   * reference_number_contains:", expense.reference_number)

    try:

        response = await zoho_client.request(

            path="/expenses",

            include_org_id=True,

            params={

                "reference_number_contains": expense.reference_number,

            },

        )

        expenses = response.json().get("expenses")

        if expenses:

            return {

                "ok": True,

                "expense": expenses[0],

            }

        return False

    except Exception as e:

        print("Is Expense Exists Error:", e)

        return {

            "ok": False,

            "error": e,

        }

async def is_expense_exists_by_description(expense: CreateExpenseZoho):

    print("- Checking if Expense exists in Zoho (by description fingerprint)...")

    fingerprint = expense.build_description_fingerprint()

    print("   * description_contains:", fingerprint)

    try:

        response = await zoho_client.request(

            path="/expenses",

            include_org_id=True,

            params={

                "description_contains": fingerprint,

            },

        )

        expenses = response.json().get("expenses")

        if expenses:

            return {

                "ok": True,

                "expense": expenses[0],

            }

        return False

    except Exception as e:

        print("Is Expense Exists By Description Error:", e)

        return {

            "ok": False,

            "error": e,

        }

async def create_expense_in_zoho(expense: CreateExpenseZoho, vendor_id: str):
    print("- Creating Expense in Zoho...")
    expense.vendor_id = vendor_id
    expense.reference_number = expense.reference_number.lower()

    # Build description fingerprint BEFORE stringifying
    expense.description = expense.build_description_fingerprint()

    # Check by description fingerprint first (higher confidence)
    is_exists_by_desc = await is_expense_exists_by_description(expense)
    if is_exists_by_desc:
        return {
            "ok": False,
            "error": "Expense already exists (matched by description fingerprint)"
        }

    # Check by reference_number second (manual entry, lower confidence)
    is_exists = await is_expense_exists(expense)
    if is_exists:
        return {
            "ok": False,
            "error": "Expense already exists (matched by reference_number)"
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

