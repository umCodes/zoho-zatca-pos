"""Receipt scanning shared by the HTTP API (POST /upload) and the MCP server.

Scanning and recording are two separate steps — the user reviews/edits the
extracted fields in between — so the image bytes are parked here under an
upload_id until the expense is created and the receipt attached to it.
"""

import base64
import time
import uuid

from app.services.mistral_services import process_img
from app.utils.qr_decoder import decode_qr_code

# Receipts that are never turned into an expense are dropped after this long,
# so abandoned scans don't accumulate in memory.
PENDING_RECEIPT_TTL = 60 * 60

_pending_receipts: dict[str, tuple[float, bytes, str, str]] = {}


def _prune_pending() -> None:
    cutoff = time.time() - PENDING_RECEIPT_TTL
    for upload_id in [k for k, v in _pending_receipts.items() if v[0] < cutoff]:
        del _pending_receipts[upload_id]


def store_pending_receipt(contents: bytes, filename: str, content_type: str) -> str:
    _prune_pending()
    upload_id = uuid.uuid4().hex
    _pending_receipts[upload_id] = (time.time(), contents, filename, content_type)
    return upload_id


def pop_pending_receipt(upload_id: str | None) -> tuple[bytes, str, str] | None:
    """Returns (bytes, filename, content_type) and forgets the receipt."""
    if not upload_id:
        return None
    entry = _pending_receipts.pop(upload_id, None)
    if entry is None:
        return None
    return entry[1], entry[2], entry[3]


class NoReceiptDataError(Exception):
    """Neither the QR code nor the OCR scan yielded invoice fields."""


async def scan_receipt(contents: bytes, mime_type: str = "image/jpeg") -> dict:
    """Extracts purchase-invoice fields from a receipt image — tries the ZATCA
    QR code first (fast, no AI cost) and falls back to OCR + LLM structuring.

    Returns {"source": "qr" | "ai", "data": {...}}. Raises ScanOverloadedError /
    ScanTimeoutError from mistral_services, or NoReceiptDataError.
    """
    qr_data = decode_qr_code(contents).get("data")
    if qr_data:
        return {"source": "qr", "data": qr_data}

    data = await process_img(base64.b64encode(contents).decode("utf-8"), mime_type=mime_type)
    if "contact_name" not in data:
        raise NoReceiptDataError("Could not extract invoice data from image")
    return {"source": "ai", "data": data}
