# services/vendors.py
from app.models.vendors_models import VendorModel
from app.services.zoho_client import zoho_post, zoho_get
from app.utils.filters import filter_fields, filter_list_fields
from app.db.database import get_db
from app.db.models import Contact
from app.db.services import create_contact, get_contacts
from app.db.schemas import ContactCreate
from sqlalchemy.exc import IntegrityError


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

    # 1. Guard: check for duplicate VAT before hitting Zoho
    db = next(get_db())
    try:
        if vendor_data.tax_reg_no:
            existing = get_contacts(db).filter(
                Contact.tax_reg_no == vendor_data.tax_reg_no
            ).first()
            if existing:
                db.close()
                return {
                    "contact_id": existing.contact_id,
                    "contact_name": existing.contact_name,
                    "tax_reg_no": existing.tax_reg_no,
                }

        # 2. Call Zoho first — we need `data` before writing to DB
        res = await zoho_post("/contacts", payload)
        data = res.json()
        print(data)

        if "contact" not in data:
            raise ValueError(
                f"Failed to create vendor: {data.get('message', 'Unknown error')}"
            )

        # 3. Persist to local DB using the contact_id returned by Zoho
        create_contact(db, ContactCreate(
            contact_id=data["contact"]["contact_id"],
            contact_name=data["contact"]["contact_name"],
            tax_reg_no=data["contact"].get("tax_reg_no"),
        ))

    except IntegrityError:
        db.rollback()
        contact_id = data["contact"]["contact_id"] if "contact" in data else "unknown"
        print(f"Pending rollback error for vendor {contact_id}, skipping.")
        raise {"message": f"Vendor with contact_id {contact_id} already exists in DB."}

    except ValueError:
        raise {
            "message": f"Failed to create vendor: {data.get('message', 'Unknown error')}"
        }

    except Exception as e:
        db.rollback()
        print(f"Unexpected error creating vendor: {e}")
        raise {"message": f"Error creating vendor: {str(e)}"}

    finally:
        db.close()

    fields_to_keep = [
        "contact_id",
        "contact_name",
        "tax_reg_no"
    ]
    return filter_fields(data["contact"], fields_to_keep)

# get vendor contact_id by tax_reg_no from db
async def get_vendor(tax_reg_no: str):
    db = next(get_db())
    try:
        existing = get_contacts(db).filter(
            Contact.tax_reg_no == tax_reg_no
        ).first()
        if existing:
            return {
                "contact_id": existing.contact_id,
                "contact_name": existing.contact_name,
                "tax_reg_no": existing.tax_reg_no,
            }
        else:
            return None
            # raise ValueError(f"Vendor with VAT no {tax_reg_no} not found in DB.")
    finally:
        db.close()



async def get_vendors():
    res = await zoho_get("/contacts", params={"contact_type": "vendor"})
    data = res.json()

    filtered = filter_list_fields(data.get("contacts", []), ["contact_id", "contact_name"])

    db = next(get_db())
    try:
        for vendor in filtered:
            existing = get_contacts(db).filter(
                Contact.contact_id == vendor["contact_id"]
            ).first()

            if not existing:
                get_vendor = await zoho_get(f"/contacts/{vendor['contact_id']}")
                vendor_detail = get_vendor.json()
                vendor_data = vendor_detail.get("contact", {})

                try:
                    create_contact(db, ContactCreate(
                        contact_id=vendor["contact_id"],
                        contact_name=vendor["contact_name"],
                        tax_reg_no=vendor_data.get("tax_reg_no"),  # .get() avoids KeyError
                    ))
                except IntegrityError:
                    print(f"Duplicate vendor {vendor['contact_id']}, skipping.")
                    db.rollback()
                except Exception as e:
                    print(f"Error syncing vendor {vendor['contact_id']}: {e}")
                    continue

        return get_contacts(db).all()

    finally:
        db.close()  # Always closes, even if an exception escapes