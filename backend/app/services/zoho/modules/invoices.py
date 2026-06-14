from decimal import Decimal
from datetime import date

from app.services.zoho.models.invoices_models import Invoice
from app.services.zoho.client import zoho_client
from app.services.openrouter_services import process_item
from app.utils.calcs import extract_vat
from app.utils.filters import filter_fields


WALK_IN_CUSTOMER_ID = "46324000000060009"

ITEM_FIELDS = [
    "name",
    "name_sec_lang",
    "sku",
    "unit",
    "description",
    "rate",
    "tax_id",
    "tax_name",
    "tax_percentage",
    "tax_type",
    "tax_status",
    "tax_country_code",
    "is_taxable",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_invoice(invoice: Invoice) -> dict:
    return {k: v for k, v in invoice.model_dump().items() if v is not None}


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

async def update_item(item_id: str, updates: dict) -> dict:
    res = await zoho_client.request(
        path=f"/items/{item_id}",
        method="PUT",
        include_org_id=True,
        json=updates,
    )
    return res.json()["item"]


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

async def get_invoices(params: dict = None) -> list:
    res = await zoho_client.request(
        path="/invoices",
        include_org_id=True,
        params=params or {},
    )
    data = res.json()
    if data.get("message") != "success":
        return { "ok": False, "error": data }
    return data["invoices"]

async def get_invoice(invoice_id: str) -> dict:
    res = await zoho_client.request(
        path=f"/invoices/{invoice_id}",
        include_org_id=True,
    )
    return res.json()["invoice"]


async def mark_invoice_as_sent(invoice_id: str) -> str:
    res = await zoho_client.request(
        path=f"/invoices/{invoice_id}/status/sent",
        method="POST",
        include_org_id=True,
    )
    return res.json()["message"]


async def create_walk_in_invoice(line_items, method: str = "Cash") -> dict:
    invoice = Invoice(
        customer_id=WALK_IN_CUSTOMER_ID,
        line_items=line_items,
        template_id="46324000000043619",
    )

    total = 0
    for item in invoice.line_items:
        total += float(Decimal(str(item.rate)) * Decimal(str(item.quantity)))
        item.rate = float(Decimal(str(item.rate)) / Decimal("1.15"))
        item.tax_percentage = 15.0
        item.tax_id = "46324000000043661"
        item.tax_name = "Standard Rate"

    # Create invoice
    res = await zoho_client.request(
        path="/invoices",
        method="POST",
        include_org_id=True,
        json=_format_invoice(invoice),
    )
    data = res.json()
    if "invoice" not in data:
        raise ValueError(f"Failed to create invoice: {data.get('message', 'Unknown error')}")

    invoice_data = filter_fields(data["invoice"], {"invoice_id", "invoice_number"})
    invoice_id = invoice_data["invoice_id"]
    invoice_number = invoice_data["invoice_number"]

    # Mark as sent
    sent_res = await zoho_client.request(
        path=f"/invoices/{invoice_id}/status/sent",
        include_org_id=True,
    )
    is_sent = sent_res.status_code in (200, 201)

    # Record payment
    payment_payload = {
        "customer_id": WALK_IN_CUSTOMER_ID,
        "payment_mode": method or "cash",
        "amount": total,
        "date": date.today().isoformat(),
        "invoices": [{"invoice_id": invoice_id, "amount_applied": total}],
    }
    payment_res = await zoho_client.request(
        path="/customerpayments",
        method="POST",
        include_org_id=True,
        json=payment_payload,
    )
    payment_data = payment_res.json()
    is_paid = "payment" in payment_data

    return {
        "invoice_id": invoice_id,
        "invoice_number": invoice_number,
        "payment_id": payment_data["payment"]["payment_id"] if is_paid else None,
        "amount": total,
        "is_sent": is_sent,
        "is_paid": is_paid,
    }


# ---------------------------------------------------------------------------
# E-invoicing / Fatoora
# ---------------------------------------------------------------------------

async def push_einvoice(invoice_id: str) -> dict:
    res = await zoho_client.request(
        path=f"/invoices/{invoice_id}/einvoice/push",
        method="POST",
        include_org_id=True,
    )
    return res.json()


async def push_to_fatoora(invoice: dict) -> bool:
    if invoice["einvoice_details"]["status"] == "pushed":
        return True

    try:
        push = await push_einvoice(invoice["invoice_id"])
        errors = push["data"]["errors"]
        if errors or push["data"]["status"] != "PASS":
            raise Exception(f"Push failed: {errors}")
        print(f"Invoice {invoice['invoice_id']} pushed successfully. ✅")
        return True
    except Exception as error:
        print(error)
        await _fix_invoice_items(invoice)
        return await push_to_fatoora(invoice)


async def _fix_invoice_items(invoice: dict) -> None:
    inv = await get_invoice(invoice["invoice_id"])
    if inv["einvoice_details"]["status"] == "pushed":
        return

    for item in inv["line_items"]:
        if item["name_sec_lang"] != "":
            continue
        print(f"Processing item '{item['name']}'...")
        processed_item = await process_item(filter_fields(item, ITEM_FIELDS))
        processed_item["rate"] = extract_vat(item)
        await update_item(item["item_id"], processed_item)
        print(f"Item '{item['description']}' updated. ✅")