import base64
import datetime as dt

import pytest
from fastapi.testclient import TestClient

from mcp.client import Client

from app.database.models import Contact, Expense
from app.database.setup import SessionLocal
from app.mcp_server.server import mcp
from app.services import receipts
from app.services.orchestrators import contact_services, expenses_services

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def seed():
    with SessionLocal() as db:
        db.add_all([
            Contact(contact_type="vendor", contact_id="v1", tax_reg_no="300000000000003", contact_name="Al Marai"),
            Contact(contact_type="vendor", contact_id="v2", tax_reg_no="311111111111113", contact_name="Panda"),
            Contact(contact_type="customer", contact_id="c1", tax_reg_no="322222222222223", contact_name="Some Customer"),
        ])
        db.add_all([
            Expense(expense_id="e1", amount=115, reference_number="inv-1", tax_reg_no="300000000000003", vendor_id="v1", date=dt.date(2026, 10, 3)),
            Expense(expense_id="e2", amount=230, reference_number="inv-2", tax_reg_no="300000000000003", vendor_id="v1", date=dt.date(2026, 11, 5)),
            Expense(expense_id="e3", amount=57.5, reference_number="inv-3", tax_reg_no="311111111111113", vendor_id="v2", date=dt.date(2026, 11, 10)),
        ])
        db.commit()


async def call(name, args=None):
    async with Client(mcp) as client:
        return await client.call_tool(name, args or {})


async def test_lists_expected_tools():
    async with Client(mcp) as client:
        tools = {t.name: t for t in (await client.list_tools()).tools}
    assert set(tools) == {
        "list_purchases", "get_purchase", "purchases_summary", "list_vendors",
        "scan_receipt", "record_purchase", "delete_purchases",
    }
    assert tools["delete_purchases"].annotations.destructive_hint is True
    assert tools["list_purchases"].annotations.read_only_hint is True


async def test_list_purchases_filters_and_orders():
    seed()
    result = await call("list_purchases", {"vendor": "marai", "date_from": "2026-11-01"})
    data = result.structured_content
    assert data["total_matching"] == 1
    assert [p["expense_id"] for p in data["purchases"]] == ["e2"]
    assert data["purchases"][0]["vendor"]["name"] == "Al Marai"

    all_rows = (await call("list_purchases")).structured_content
    assert [p["expense_id"] for p in all_rows["purchases"]] == ["e3", "e2", "e1"]


async def test_summary_by_vendor_and_month():
    seed()
    by_vendor = (await call("purchases_summary")).structured_content
    assert by_vendor["grand_total"] == 402.5
    assert by_vendor["groups"][0]["vendor"]["vendor_id"] == "v1"
    assert by_vendor["groups"][0]["total"] == 345.0

    by_month = (await call("purchases_summary", {"group_by": "month"})).structured_content
    assert [(g["month"], g["count"]) for g in by_month["groups"]] == [("2026-11", 2), ("2026-10", 1)]


async def test_list_vendors_excludes_customers():
    seed()
    vendors = (await call("list_vendors")).structured_content["vendors"]
    assert {v["vendor_id"]: (v["purchase_count"], v["total_spent"]) for v in vendors} == {
        "v1": (2, 345.0),
        "v2": (1, 57.5),
    }


async def test_scan_then_record_creates_vendor_expense_and_attaches_receipt(monkeypatch):
    async def fake_scan(contents, mime_type="image/jpeg"):
        assert contents == b"fake-image"
        return {"source": "qr", "data": {"contact_name": "New Vendor", "tax_reg_no": "399999999999993", "amount": 92, "date": "2026-11-18"}}

    async def fake_create_contact(contact):
        return {"ok": True, "contact": {"contact_id": "v9", "contact_type": "vendor", "tax_reg_no": contact.tax_reg_no, "contact_name": contact.contact_name}}

    async def fake_create_expense(expense, vendor_id):
        return {"ok": True, "expense": {"expense_id": "e9", "tax_reg_no": expense.tax_reg_no, "amount": expense.amount,
                                         "reference_number": expense.reference_number.lower(), "date": expense.date, "vendor_id": vendor_id}}

    attached = {}

    async def fake_attach(expense_id, image_bytes, filename, content_type):
        attached.update(expense_id=expense_id, image_bytes=image_bytes, content_type=content_type)
        return {"ok": True}

    # Postgres accepts the ISO date string the orchestrator stores; SQLite's
    # Date type does not, so convert it on the way into the test database.
    real_create_expense_db = expenses_services.create_expense_db

    def sqlite_create_expense_db(db, expense):
        return real_create_expense_db(db=db, expense=expense.model_copy(update={"date": dt.date.fromisoformat(expense.date)}))

    monkeypatch.setattr(expenses_services, "create_expense_db", sqlite_create_expense_db)
    monkeypatch.setattr("app.mcp_server.server.scan_receipt_contents", fake_scan)
    monkeypatch.setattr(contact_services, "create_contact_in_zoho", fake_create_contact)
    monkeypatch.setattr(expenses_services, "create_expense_in_zoho", fake_create_expense)
    monkeypatch.setattr(expenses_services, "attach_expense_receipt", fake_attach)

    scan = (await call("scan_receipt", {"image_base64": "data:image/png;base64," + base64.b64encode(b"fake-image").decode()})).structured_content
    assert scan["source"] == "qr"

    recorded = await call("record_purchase", {
        "amount": 92, "reference_number": "INV-77", "date": "2026-11-18",
        "tax_reg_no": "399999999999993", "contact_name": "New Vendor", "upload_id": scan["upload_id"],
    })
    assert not recorded.is_error, recorded
    assert recorded.structured_content["receipt_attached"] is True
    assert attached == {"expense_id": "e9", "image_bytes": b"fake-image", "content_type": "image/png"}

    with SessionLocal() as db:
        assert db.query(Contact).filter_by(contact_id="v9").one().contact_name == "New Vendor"
        assert db.query(Expense).filter_by(expense_id="e9").one().reference_number == "inv-77"

    # The receipt is consumed once used.
    assert receipts.pop_pending_receipt(scan["upload_id"]) is None


async def test_record_purchase_surfaces_zoho_duplicate_as_tool_error(monkeypatch):
    seed()

    async def fake_create_expense(expense, vendor_id):
        return {"ok": False, "error": "Expense already exists (matched by reference_number)"}

    monkeypatch.setattr(expenses_services, "create_expense_in_zoho", fake_create_expense)
    result = await call("record_purchase", {"amount": 115, "reference_number": "inv-1", "date": "2026-10-03", "tax_reg_no": "300000000000003"})
    assert result.is_error
    assert "already exists" in result.content[0].text


async def test_scan_receipt_rejects_bad_input():
    both = await call("scan_receipt", {"image_base64": "aGk=", "image_url": "https://x/y.jpg"})
    assert both.is_error
    http = await call("scan_receipt", {"image_url": "http://example.com/r.jpg"})
    assert http.is_error and "https" in http.content[0].text


async def test_delete_purchases_reports_each_outcome(monkeypatch):
    seed()

    async def fake_delete(expense_id):
        return {"ok": True} if expense_id == "e1" else {"ok": False, "error": {"code": 1, "message": "locked"}}

    monkeypatch.setattr(expenses_services, "delete_expense_in_zoho", fake_delete)
    data = (await call("delete_purchases", {"expense_ids": ["e1", "e2", "nope"]})).structured_content
    assert data == {"deleted": ["e1"], "not_found": ["nope"], "failed": [{"expense_id": "e2", "error": "locked"}]}
    with SessionLocal() as db:
        assert {e.expense_id for e in db.query(Expense)} == {"e2", "e3"}


def test_http_endpoint_requires_bearer_token(monkeypatch):
    async def no_refresh():
        return None

    monkeypatch.setattr("app.middlewares.token_refresh.refresh_token_if_needed", no_refresh)
    from app.main import app

    init = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}}
    headers = {"accept": "application/json, text/event-stream", "content-type": "application/json"}

    with TestClient(app) as client:
        assert client.post("/mcp", json=init, headers=headers).status_code == 401
        bad = client.post("/mcp", json=init, headers={**headers, "authorization": "Bearer nope"})
        assert bad.status_code == 401

        auth = {**headers, "authorization": "Bearer test-mcp-key", "mcp-protocol-version": "2025-06-18"}
        ok = client.post("/mcp", json=init, headers=auth)
        assert ok.status_code == 200, ok.text
        assert ok.json()["result"]["serverInfo"]["name"] == "zoho-purchases"

        listed = client.post("/mcp", json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, headers=auth)
        assert listed.status_code == 200, listed.text
        assert "record_purchase" in {t["name"] for t in listed.json()["result"]["tools"]}

        # The rest of the API is unaffected.
        assert client.get("/health").status_code == 200
