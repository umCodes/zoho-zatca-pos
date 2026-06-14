from app.services.zoho.models.expenses_models import CreateExpenseZoho
from app.services.zoho.models.contacts_models import CreateContactZoho

from app.database.schemas import ContactCreate
from app.database.services import get_contact_by_tax_reg_no_db, create_contact_db

from app.services.zoho.modules.contacts import create_contact_in_zoho


async def resolve_vendor(db, expense: CreateExpenseZoho):
    print("- Resolving Vendor...")

    # Check if vendor exists in database
    vendor = get_contact_by_tax_reg_no_db(db=db, tax_reg_no=expense.tax_reg_no)
    if vendor: 
        return {"ok": True, "contact_id": vendor.contact_id}

    # If vendor doesn't exist and contact_name not provided, return error
    if not expense.contact_name:
        return {
            "ok": False,
            "from": "db",
            "message": "Vendor doesn't exist. Provide contact_name to create vendor."
        }

    # Otherwise create vendor in zoho
    created = await create_contact_in_zoho(CreateContactZoho(
        contact_type="vendor",
        contact_name=expense.contact_name,
        tax_reg_no=expense.tax_reg_no,
        tax_treatment="vat_registered" if expense.tax_reg_no else "vat_not_registered",
    ))
    # If zoho creation failed, return error
    if created["ok"] is False:
        return created

    # Save vendor to database and return vendor as dict
    vendor = create_contact_db(db, contact=ContactCreate(**created["contact"]))
    return vendor.model_dump()
