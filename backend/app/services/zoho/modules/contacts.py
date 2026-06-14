from httpx import HTTPStatusError
from app.services.zoho.client import zoho_client
from app.utils.filters import filter_list_fields, filter_fields

from app.services.zoho.models.contacts_models import CreateContactZoho

async def get_contacts(params={}):
    try:
        response = await zoho_client.request(path="/contacts", params=params, include_org_id=True)
        data = response.json()

        if data.get("message") != "success":
            return { "ok": False, "error": data }

        return {
            "ok": True,
            "contacts": filter_list_fields(
                data=data["contacts"], 
                fields_to_keep=[
                    "contact_id",
                    "contact_type",
                    "tax_reg_no",
                    "contact_name",
                ])
        }
    except HTTPStatusError as e:
        print(e)
        return {
            "ok": False,
            "from": "zoho",
            "error": e
        }

async def get_contact(id: str):
    try:
        response = await zoho_client.request(path=f"/contacts/{id}",include_org_id=True)
        data = response.json()

        if data.get("message") != "success":
            return { "ok": False, "error": data }

        return {
            "ok": True,
            "contact": filter_fields(
                data=data["contact"], 
                fields_to_keep=[
                    "contact_id",
                    "contact_type",
                    "tax_reg_no",
                    "contact_name",
                ])
        }
    except HTTPStatusError as e:
        print(e)
        return {
            "ok": False,
            "from": "zoho",
            "error": e
        }

async def create_contact_in_zoho(contact: CreateContactZoho):
    print("- Creating Contact in Zoho...")
    try:
        response = await zoho_client.request(
            method="POST",
            path="/contacts",
            json={
                # "contact_id": contact,
                "contact_type": contact.contact_type,
                "tax_reg_no": contact.tax_reg_no,
                "contact_name": contact.contact_name,
            },
            include_org_id=True
        )
        data = response.json()

        if data.get("code") != 0 or not data.get("contact"):
            return { "ok": False, "error": data }

        return {
            "ok": True,
            "contact": filter_fields(
                data=data["contact"], 
                fields_to_keep=[
                    "contact_id",
                    "contact_type",
                    "tax_reg_no",
                    "contact_name",
                ])
        }
    except HTTPStatusError as e:
        print(e)
        return {
            "ok": False,
            "from": "zoho",
            "error": e
        }


    