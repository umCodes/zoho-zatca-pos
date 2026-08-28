import time
from httpx import HTTPStatusError
from app.services.zoho.client import zoho_client
from app.utils.filters import filter_list_fields, filter_fields

from app.services.zoho.models.contacts_models import CreateContactZoho, CreateCustomerDetailedZoho

# ── Customer cache ──────────────────────────────────────────────────────
# Short-lived: refetched after CUSTOMERS_CACHE_TTL seconds, and wiped
# immediately whenever a new customer is created so the list stays current.
CUSTOMERS_CACHE_TTL = 60
_customers_cache: list[dict] = []
_customers_cache_at: float = 0


def invalidate_customers_cache() -> None:
    global _customers_cache, _customers_cache_at
    _customers_cache = []
    _customers_cache_at = 0


async def get_customers(search: str = "") -> dict:
    global _customers_cache, _customers_cache_at

    is_stale = (time.time() - _customers_cache_at) > CUSTOMERS_CACHE_TTL
    if not _customers_cache or is_stale:
        result = await get_contacts({"contact_type": "customer"})
        if not result["ok"]:
            return result
        _customers_cache = result["contacts"]
        _customers_cache_at = time.time()

    customers = _customers_cache
    if search:
        needle = search.lower()
        customers = [
            c for c in customers
            if needle in (c.get("contact_name") or "").lower()
            or needle in (c.get("tax_reg_no") or "").lower()
        ]

    return {"ok": True, "customers": customers}


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


CUSTOMER_DETAIL_FIELDS = [
    "contact_id",
    "contact_type",
    "contact_name",
    "contact_name_sec_lang",
    "company_name",
    "tax_reg_no",
    "tax_treatment",
    "buyer_id_label",
    "buyer_id_value",
    "email",
    "phone",
    "mobile",
    "currency_code",
    "payment_terms_label",
    "credit_limit",
    "outstanding_receivable_amount",
    "billing_address",
    "shipping_address",
    "status",
]


async def get_customer(id: str) -> dict:
    """Fetch a single customer with the fuller detail set (address, contact info,
    balance) — meant for a "view customer" screen, not the trimmed list/search shape."""
    try:
        response = await zoho_client.request(path=f"/contacts/{id}", include_org_id=True)
        data = response.json()

        if data.get("message") != "success":
            return {"ok": False, "error": data}

        contact = data["contact"]
        if contact.get("contact_type") != "customer":
            return {"ok": False, "error": "Not a customer"}

        return {
            "ok": True,
            "customer": filter_fields(data=contact, fields_to_keep=CUSTOMER_DETAIL_FIELDS),
        }
    except HTTPStatusError as e:
        print(e)
        return {
            "ok": False,
            "from": "zoho",
            "error": e,
        }

async def create_customer_detailed_in_zoho(customer: CreateCustomerDetailedZoho) -> dict:
    """Creates a customer with the full bilingual ZATCA field set (name, VAT,
    CRN via buyer_id_label/value, and a fully bilingual billing address) —
    every field here is a verified native Zoho field, not a custom field."""
    print("- Creating detailed Customer in Zoho...")
    payload = {
        "contact_type": "customer",
        "contact_name": customer.contact_name,
        "contact_name_sec_lang": customer.contact_name_sec_lang,
        "company_name": customer.contact_name,
        "tax_treatment": customer.tax_treatment,
        "tax_reg_no": customer.tax_reg_no,
        "buyer_id_label": customer.buyer_id_label,
        "buyer_id_value": customer.buyer_id_value,
        # Phone only persists via billing_address.phone (verified against the
        # live API — there is no top-level contact phone field on create).
        "billing_address": customer.billing_address.to_zoho(customer.country_code, phone=customer.phone),
    }

    # Drop None values — Zoho treats an explicit null differently from an
    # omitted key on some fields, so only send what was actually provided.
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        response = await zoho_client.request(
            method="POST",
            path="/contacts",
            json=payload,
            include_org_id=True,
        )
        data = response.json()

        if data.get("code") != 0 or not data.get("contact"):
            return {"ok": False, "error": data}

        invalidate_customers_cache()

        return {
            "ok": True,
            "contact": filter_fields(data=data["contact"], fields_to_keep=CUSTOMER_DETAIL_FIELDS),
        }
    except HTTPStatusError as e:
        print(e)
        return {
            "ok": False,
            "from": "zoho",
            "error": e,
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

        if contact.contact_type == "customer":
            invalidate_customers_cache()

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
