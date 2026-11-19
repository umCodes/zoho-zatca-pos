"""MCP server for the purchases (expense) recording system.

Exposes the same flow the Telegram bot and admin app use — scan a receipt,
review the fields, record it as a Zoho Books expense — plus read-only views
over the local Postgres mirror of recorded purchases and vendors.

Reads come from Postgres (fast, no Zoho API quota); writes go through the
existing orchestrators so vendor resolution, duplicate detection, receipt
attachment and the Postgres mirror behave exactly as they do elsewhere.
"""

import base64
import binascii
from collections import defaultdict
import datetime as dt
from typing import Annotated, Any, Literal

import httpx
from pydantic import Field, ValidationError
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from app.database.models import Contact, Expense
from app.database.setup import SessionLocal
from app.services.mistral_services import ScanOverloadedError, ScanTimeoutError
from app.services.orchestrators.expenses_services import create_expense, delete_expenses
from app.services.receipts import (
    NoReceiptDataError,
    pop_pending_receipt,
    scan_receipt as scan_receipt_contents,
    store_pending_receipt,
)
from app.services.zoho.models.expenses_models import CreateExpenseZoho
from app.services.zoho.modules.expenses import get_expense

MAX_RECEIPT_BYTES = 10 * 1024 * 1024

INSTRUCTIONS = """\
Records and reviews purchase invoices (Zoho Books expenses) for a Saudi retail
business. Amounts are in SAR and VAT-inclusive (15%).

Recording a purchase:
1. If you have the receipt as base64 or an https URL, call scan_receipt. It reads
   the ZATCA QR code (or falls back to OCR) and returns the fields plus an
   upload_id. If you can only see the image yourself, read the fields from it.
2. Show the extracted vendor, VAT number, amount, invoice number and date to the
   user and let them correct anything before recording.
3. Call record_purchase with the confirmed fields (and the upload_id, so the
   receipt image is attached in Zoho). New vendors are created automatically,
   matched by VAT number. Duplicates are rejected.

list_purchases, purchases_summary and list_vendors read the local mirror of
what has been recorded. delete_purchases removes expenses from Zoho and the
mirror and cannot be undone — confirm with the user first.
"""

mcp = MCPServer(
    name="zoho-purchases",
    title="Purchases",
    instructions=INSTRUCTIONS,
    version="1.0.0",
)

READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=False)


# ─── Helpers ──────────────────────────────────────────────────────────────


def _vendor_dict(vendor: Contact | None) -> dict[str, Any] | None:
    if vendor is None:
        return None
    return {
        "vendor_id": vendor.contact_id,
        "name": vendor.contact_name,
        "tax_reg_no": vendor.tax_reg_no,
    }


def _purchase_dict(expense: Expense) -> dict[str, Any]:
    return {
        "expense_id": expense.expense_id,
        "date": expense.date.isoformat(),
        "amount": float(expense.amount),
        "reference_number": expense.reference_number,
        "tax_reg_no": expense.tax_reg_no,
        "vendor": _vendor_dict(expense.vendor),
    }


def _filtered_purchases(db, vendor: str | None, date_from: dt.date | None, date_to: dt.date | None):
    query = db.query(Expense).options(joinedload(Expense.vendor))
    if vendor:
        needle = f"%{vendor.strip()}%"
        query = query.join(Expense.vendor).filter(
            or_(Contact.contact_name.ilike(needle), Contact.tax_reg_no.ilike(needle))
        )
    if date_from:
        query = query.filter(Expense.date >= date_from)
    if date_to:
        query = query.filter(Expense.date <= date_to)
    return query


def _error_text(result: dict) -> str:
    error = result.get("error") or result.get("message") or result
    if isinstance(error, dict):
        return error.get("message") or str(error)
    return str(error)


async def _load_receipt(image_base64: str | None, image_url: str | None, mime_type: str | None) -> tuple[bytes, str, str]:
    if bool(image_base64) == bool(image_url):
        raise ToolError("Provide exactly one of image_base64 or image_url.")

    if image_base64:
        payload = image_base64.strip()
        if payload.startswith("data:"):
            header, _, payload = payload.partition(",")
            mime_type = mime_type or header[5:].split(";")[0] or None
        try:
            contents = base64.b64decode(payload, validate=True)
        except (binascii.Error, ValueError):
            raise ToolError("image_base64 is not valid base64.")
        filename = "receipt"
    else:
        if not image_url.lower().startswith("https://"):
            raise ToolError("image_url must be an https:// URL.")
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(image_url)
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise ToolError(f"Could not download the receipt: {e}")
        contents = response.content
        mime_type = mime_type or response.headers.get("content-type", "").split(";")[0] or None
        filename = image_url.rsplit("/", 1)[-1].split("?")[0] or "receipt"

    if not contents:
        raise ToolError("The receipt image is empty.")
    if len(contents) > MAX_RECEIPT_BYTES:
        raise ToolError("The receipt image is larger than 10 MB.")
    return contents, filename, mime_type or "image/jpeg"


# ─── Tools ────────────────────────────────────────────────────────────────


@mcp.tool(title="List purchases", annotations=READ_ONLY)
def list_purchases(
    vendor: Annotated[str | None, Field(description="Filter by vendor name or VAT number (partial match).")] = None,
    date_from: Annotated[dt.date | None, Field(description="Earliest invoice date, inclusive (YYYY-MM-DD).")] = None,
    date_to: Annotated[dt.date | None, Field(description="Latest invoice date, inclusive (YYYY-MM-DD).")] = None,
    limit: Annotated[int, Field(ge=1, le=500, description="Maximum number of purchases to return.")] = 50,
) -> dict[str, Any]:
    """List recorded purchase invoices, newest first, with their vendor."""
    with SessionLocal() as db:
        query = _filtered_purchases(db, vendor, date_from, date_to)
        total = query.count()
        rows = query.order_by(Expense.date.desc(), Expense.id.desc()).limit(limit).all()
        return {
            "total_matching": total,
            "returned": len(rows),
            "purchases": [_purchase_dict(row) for row in rows],
        }


@mcp.tool(title="Get purchase", annotations=ToolAnnotations(read_only_hint=True))
async def get_purchase(
    expense_id: Annotated[str, Field(description="The Zoho expense_id of the purchase.")],
) -> dict[str, Any]:
    """Get one recorded purchase, including its current state in Zoho Books."""
    with SessionLocal() as db:
        expense = (
            db.query(Expense)
            .options(joinedload(Expense.vendor))
            .filter(Expense.expense_id == expense_id)
            .first()
        )
        local = _purchase_dict(expense) if expense else None

    zoho = await get_expense(expense_id)
    if local is None and not zoho.get("ok"):
        raise ToolError(f"No purchase found with expense_id {expense_id}.")

    return {
        "purchase": local,
        "in_local_records": local is not None,
        "zoho": zoho.get("expense") if zoho.get("ok") else None,
        "zoho_error": None if zoho.get("ok") else _error_text(zoho),
    }


@mcp.tool(title="Purchases summary", annotations=READ_ONLY)
def purchases_summary(
    date_from: Annotated[dt.date | None, Field(description="Earliest invoice date, inclusive (YYYY-MM-DD).")] = None,
    date_to: Annotated[dt.date | None, Field(description="Latest invoice date, inclusive (YYYY-MM-DD).")] = None,
    group_by: Annotated[Literal["vendor", "month"], Field(description="Group totals by vendor or by calendar month.")] = "vendor",
    vendor: Annotated[str | None, Field(description="Only include vendors matching this name or VAT number.")] = None,
) -> dict[str, Any]:
    """Total spend and purchase counts over a period, grouped by vendor or month.
    Amounts are VAT-inclusive SAR."""
    with SessionLocal() as db:
        rows = _filtered_purchases(db, vendor, date_from, date_to).all()

        groups: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "total": 0.0})
        for row in rows:
            if group_by == "month":
                key = row.date.strftime("%Y-%m")
                groups[key]["month"] = key
            else:
                key = row.vendor_id
                groups[key]["vendor"] = _vendor_dict(row.vendor)
            groups[key]["count"] += 1
            groups[key]["total"] += float(row.amount)

    ordered = sorted(groups.values(), key=lambda g: g["month"], reverse=True) if group_by == "month" \
        else sorted(groups.values(), key=lambda g: g["total"], reverse=True)
    for group in ordered:
        group["total"] = round(group["total"], 2)

    return {
        "date_from": date_from.isoformat() if date_from else None,
        "date_to": date_to.isoformat() if date_to else None,
        "purchase_count": len(rows),
        "grand_total": round(sum(float(r.amount) for r in rows), 2),
        "groups": ordered,
    }


@mcp.tool(title="List vendors", annotations=READ_ONLY)
def list_vendors(
    query: Annotated[str | None, Field(description="Filter by vendor name or VAT number (partial match).")] = None,
    limit: Annotated[int, Field(ge=1, le=500)] = 100,
) -> dict[str, Any]:
    """List known vendors with how many purchases are recorded against each and
    the total spent."""
    with SessionLocal() as db:
        stmt = (
            db.query(
                Contact,
                func.count(Expense.id).label("purchase_count"),
                func.coalesce(func.sum(Expense.amount), 0).label("total_spent"),
            )
            .outerjoin(Expense, Expense.vendor_id == Contact.contact_id)
            .filter(Contact.contact_type == "vendor")
            .group_by(Contact.id)
        )
        if query:
            needle = f"%{query.strip()}%"
            stmt = stmt.filter(or_(Contact.contact_name.ilike(needle), Contact.tax_reg_no.ilike(needle)))
        rows = stmt.order_by(Contact.contact_name).limit(limit).all()

        return {
            "vendors": [
                {
                    **_vendor_dict(contact),
                    "purchase_count": count,
                    "total_spent": round(float(total), 2),
                }
                for contact, count, total in rows
            ]
        }


@mcp.tool(
    title="Scan receipt",
    annotations=ToolAnnotations(read_only_hint=True, open_world_hint=True),
)
async def scan_receipt(
    image_base64: Annotated[str | None, Field(description="The receipt image or PDF as base64 (a data: URI is also accepted).")] = None,
    image_url: Annotated[str | None, Field(description="An https URL to download the receipt image or PDF from.")] = None,
    mime_type: Annotated[str | None, Field(description="e.g. image/jpeg, image/png, application/pdf. Inferred when omitted.")] = None,
) -> dict[str, Any]:
    """Extract purchase-invoice fields (vendor, VAT number, amount, invoice
    number, date) from a receipt. Reads the ZATCA QR code when present,
    otherwise runs OCR. Nothing is recorded — show the result to the user, then
    pass the confirmed fields and the returned upload_id to record_purchase."""
    contents, filename, mime = await _load_receipt(image_base64, image_url, mime_type)

    try:
        scanned = await scan_receipt_contents(contents, mime_type=mime)
    except ScanOverloadedError as e:
        raise ToolError(f"The receipt scanner is overloaded, try again shortly: {e}")
    except ScanTimeoutError as e:
        raise ToolError(f"The receipt scan timed out: {e}")
    except NoReceiptDataError as e:
        raise ToolError(str(e))
    except Exception as e:
        raise ToolError(f"Receipt scan failed: {e}")

    upload_id = store_pending_receipt(contents, filename, mime)
    return {**scanned, "upload_id": upload_id}


@mcp.tool(
    title="Record purchase",
    annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=True),
)
async def record_purchase(
    amount: Annotated[float, Field(gt=0, description="Invoice total in SAR, VAT-inclusive.")],
    reference_number: Annotated[str, Field(min_length=1, description="The vendor's invoice number.")],
    date: Annotated[dt.date, Field(description="Invoice date (YYYY-MM-DD).")],
    tax_reg_no: Annotated[str | None, Field(description="Vendor VAT registration number (15 digits). Used to find or create the vendor.")] = None,
    contact_name: Annotated[str | None, Field(description="Vendor name — required if the vendor is new. Arabic name preferred when available.")] = None,
    upload_id: Annotated[str | None, Field(description="upload_id from scan_receipt, to attach the receipt image in Zoho.")] = None,
) -> dict[str, Any]:
    """Record a purchase invoice as an expense in Zoho Books. Finds the vendor
    by VAT number, or creates it from contact_name. Rejects duplicates (same
    vendor, date and total, or same invoice number)."""
    try:
        expense = CreateExpenseZoho(
            amount=amount,
            reference_number=reference_number,
            date=date.isoformat(),
            tax_reg_no=tax_reg_no or None,
            contact_name=contact_name or None,
            upload_id=upload_id,
        )
    except ValidationError as e:
        raise ToolError(str(e))

    image = pop_pending_receipt(upload_id)
    result = await create_expense(
        expense=expense,
        image_bytes=image[0] if image else None,
        image_filename=image[1] if image else None,
        image_content_type=image[2] if image else None,
    )
    if not result.get("ok"):
        raise ToolError(f"Purchase not recorded: {_error_text(result)}")

    return {
        "recorded": True,
        "expense": result["expense"],
        "receipt_attached": image is not None,
        "receipt_note": None if image or not upload_id else "upload_id was unknown or expired; no receipt attached.",
    }


@mcp.tool(
    title="Delete purchases",
    annotations=ToolAnnotations(read_only_hint=False, destructive_hint=True, idempotent_hint=True, open_world_hint=True),
)
async def delete_purchases(
    expense_ids: Annotated[list[str], Field(min_length=1, description="Zoho expense_ids to delete.")],
) -> dict[str, Any]:
    """Permanently delete purchases from Zoho Books and the local records.
    Cannot be undone — confirm with the user before calling."""
    result = await delete_expenses(expense_ids=expense_ids)
    return {
        "deleted": result["deleted"],
        "not_found": result["not_found"],
        "failed": [
            {"expense_id": f["expense_id"], "error": _error_text(f)} for f in result["failed"]
        ],
    }
