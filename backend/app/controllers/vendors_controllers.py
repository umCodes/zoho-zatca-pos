# services/vendors.py
from app.models.vendors_models import VendorModel
from app.services.zoho_client import zoho_post
from app.utils.filters import filter_fields

async def create_vendor(vendor_data: VendorModel) -> dict:
    payload = {
        "contact_type": vendor_data.contact_type,
        "contact_name": vendor_data.contact_name,
        "company_name": vendor_data.company_name,
        "tax_treatment": vendor_data.tax_treatment,
        "country_code": vendor_data.country_code,
    }

    if vendor_data.tax_treatment == "vat_registered":
        payload["tax_reg_no"] = vendor_data.tax_reg_no

    res = await zoho_post("/contacts", payload)
    data = res.json()
    print(data)

    if "contact" not in data:
        raise ValueError(f"Failed to create vendor: {data.get('message', 'Unknown error')}")

    fields_to_keep = [
        "contact_id",
        "contact_type",
        "contact_name",
        "company_name",
        "tax_treatment",
        "tax_reg_no",
        "country_code",
    ]

    return filter_fields(data["contact"], fields_to_keep)