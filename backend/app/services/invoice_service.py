from decimal import Decimal
from datetime import date

from app.models.invoice import Invoice
from app.services.zoho_client import zoho_post
from app.utils.filters import filter_fields, filter_list_fields

WALK_IN_CUSTOMER_ID = "46324000000060009"

def format_invoice(invoice: Invoice):
    return {k: v for k, v in invoice.model_dump().items() if v is not None}



async def create_walk_in_invoice(line_items, method: str = "Cash"):
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
    res = await zoho_post("/invoices", format_invoice(invoice))
    data = res.json()
    if "invoice" not in data:
        raise ValueError(f"Failed to create invoice: {data.get('message', 'Unknown error')}")

    invoice_data = filter_fields(data["invoice"], {"invoice_id", "invoice_number"})
    invoice_id = invoice_data["invoice_id"]
    invoice_number = invoice_data["invoice_number"]
    # Mark as sent
    res = await zoho_post(f"/invoices/{invoice_id}/status/sent")
    
    is_sent = True if res.status_code in (200, 201) else False 

    # Record payment
    payment_payload = {
        "customer_id": WALK_IN_CUSTOMER_ID,
        "payment_mode": method or "cash",
        "amount": total,
        "date": date.today().isoformat(),
        "invoices": [
            {
                "invoice_id": invoice_id,
                "amount_applied": total,
            }
        ],
    }
    res = await zoho_post("/customerpayments", payment_payload)
    payment_data = res.json()
    is_paid = True if "payment" in payment_data else False
    return {
        "invoice_id": invoice_id,
        "invoice_number": invoice_number,
        "payment_id": payment_data["payment"]["payment_id"],
        "amount": total,
        "is_sent": is_sent,
        "is_paid": is_paid,
    }