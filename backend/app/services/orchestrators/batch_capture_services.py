"""Scan-and-record for a single invoice image, in one request.

Used by the admin app's multi-image upload: the app sends images one at a
time and gets back a per-image outcome, so one bad image never stops the
rest of the batch. Every outcome — including failures — is returned as data
(never raised), so the caller can show it next to that image.

QR codes are deliberately not read here: the ZATCA QR never carries the
invoice number, so the AI scan is needed for every photo anyway and reads
all the other fields too. Skipping the OpenCV decode also keeps the work
off this small server (0.5 CPU / 512 MB) — OCR and field extraction happen
at Mistral/OpenRouter. The client shrinks images before sending.
"""
import base64
import re

from pydantic import ValidationError

from app.services.mistral_services import ScanOverloadedError, ScanTimeoutError, process_img
from app.services.orchestrators.expenses_services import create_expense
from app.services.zoho.models.expenses_models import CreateExpenseZoho

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _result(status: str, data: dict, source: str | None, *, code: str | None = None,
            message: str | None = None, expense: dict | None = None) -> dict:
    out = {"status": status, "source": source, "data": data}
    if expense is not None:
        out["expense"] = expense
    if code or message:
        out["error"] = {"code": code or "generic", "message": message or ""}
    return out


def _error_message(error) -> str:
    if isinstance(error, dict):
        return str(error.get("message") or error.get("error") or error)
    return str(error)


async def scan_and_record_expense(
    contents: bytes,
    filename: str,
    content_type: str,
    fields: dict | None = None,
) -> dict:
    if fields:
        # The user corrected the fields by hand (after an earlier failed
        # attempt) — record those as-is, no scan needed.
        data = {k: fields.get(k) for k in ("contact_name", "tax_reg_no", "amount", "reference_number", "date")}
        data = {k: v for k, v in data.items() if v not in (None, "")}
        return await _record(data, "manual", None, contents, filename, content_type)

    # AI scan — reads every field, including the invoice number.
    ai_data: dict = {}
    ai_error: tuple[str, str] | None = None
    try:
        b64 = base64.b64encode(contents).decode("utf-8")
        parsed = await process_img(b64, mime_type=content_type)
        del b64
        ai_data = parsed if isinstance(parsed, dict) else {}
    except ScanOverloadedError as e:
        ai_error = ("overloaded", str(e))
    except ScanTimeoutError as e:
        ai_error = ("timeout", str(e))
    except Exception as e:
        ai_error = ("generic", f"Invoice scan failed: {e}")

    data = {k: ai_data.get(k) for k in ("contact_name", "tax_reg_no", "amount", "reference_number", "date")}
    data = {k: v for k, v in data.items() if v not in (None, "")}
    source = "ai" if ai_data else None
    return await _record(data, source, ai_error, contents, filename, content_type)


async def _record(data: dict, source: str | None, ai_error: tuple[str, str] | None,
                  contents: bytes, filename: str, content_type: str) -> dict:
    if isinstance(data.get("date"), str):
        data["date"] = data["date"].split("T")[0].strip()

    # 3. Everything needed to record it?
    missing = [f for f in ("contact_name", "reference_number", "date") if not data.get(f)]
    try:
        if float(data.get("amount") or 0) <= 0:
            missing.append("amount")
    except (TypeError, ValueError):
        missing.append("amount")

    if missing:
        if ai_error:
            return _result("failed", data, source, code=ai_error[0], message=ai_error[1])
        return _result("failed", data, source, code="missing_fields",
                       message="Could not read: " + ", ".join(missing))

    if not _DATE_RE.match(data["date"]):
        return _result("failed", data, source, code="invalid_date",
                       message=f"Unrecognized date: {data['date']}")

    try:
        expense = CreateExpenseZoho(
            contact_name=str(data["contact_name"]),
            tax_reg_no=str(data["tax_reg_no"]) if data.get("tax_reg_no") else None,
            amount=float(data["amount"]),
            reference_number=str(data["reference_number"]).strip(),
            date=data["date"],
        )
    except ValidationError as e:
        return _result("failed", data, source, code="invalid", message=str(e.errors()[0].get("msg", e)))

    # 4. Record it (vendor lookup/creation, Zoho expense, receipt, DB mirror).
    try:
        result = await create_expense(
            expense=expense,
            image_bytes=contents,
            image_filename=filename,
            image_content_type=content_type,
        )
    except Exception as e:
        print(f" * Recording failed: {e}")
        return _result("failed", data, source, code="record_failed", message=str(e))

    if result.get("ok"):
        return _result("recorded", data, source, expense=result.get("expense"))
    if result.get("duplicate"):
        return _result("duplicate", data, source)
    return _result("failed", data, source, code="record_failed",
                   message=_error_message(result.get("error") or result.get("message") or result))
