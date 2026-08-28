# Zoho ZATCA POS

A point-of-sale system for a Saudi retail business, built on top of **Zoho Books**. It rings up walk-in sales as compliant Zoho invoices, pushes them to **ZATCA** (Saudi e-invoicing) via Zoho's e-invoice gateway, and captures purchase expenses from receipt photos through a **Telegram bot**.

## What it does

**1. Point of sale (web)**
A cashier-facing cart UI: search or barcode-scan items, adjust quantity/price, choose Cash or Card, submit. Submitting creates a walk-in invoice in Zoho Books (VAT applied at 15%), marks it sent, and records the payment — then the invoice PDF can be opened/printed immediately.

**2. ZATCA e-invoice push**
A pull job (`GET /push-invoices`) fetches recent Zoho invoices and submits each one to ZATCA's Fatoora gateway through Zoho. If a push fails because an item is missing its required Arabic/English bilingual name, the backend generates the missing translation with an LLM, updates the item in Zoho, and retries automatically.

**3. Expense capture (Telegram bot)**
Staff send a photo of a purchase receipt to a Telegram bot. The bot reads it either by decoding the receipt's ZATCA QR code or, if that's not usable, by running it through Gemini vision OCR. It shows back the parsed vendor, amount, date, and VAT number for confirmation (in Arabic or Amharic), then creates the vendor (if new) and the expense in Zoho Books, mirroring both into a local Postgres database to prevent duplicates.

## How it's put together

- **Backend** — FastAPI (Python), deployed on Render. All Zoho Books access goes through one internal client (`services/zoho/`); ZATCA is never called directly — submission happens via Zoho's `/einvoice/push` endpoint. A single shared password (`x-password` header) gates the API instead of per-user accounts.
- **Frontend** — React 19 + TypeScript + Vite, a single-screen cart UI (no router). Supports English, Arabic (RTL), and Amharic. It only talks to a handful of endpoints — items, walk-in invoice, invoice PDF, password check — everything else (vendors, expenses, Zoho IDs) is decided server-side.
- **Database** — Postgres, used as a local mirror of Zoho contacts and expenses so the expense-capture flow can dedupe without round-tripping Zoho on every check. Zoho Books remains the system of record.
- **AI services** — Gemini (receipt photo → structured invoice data, with a 2-key fallback) and OpenRouter (normalizes item names into the bilingual Arabic/English form ZATCA requires).

## Project layout

```
backend/
  app/
    routes/          FastAPI route handlers (thin — delegate to controllers/services)
    controllers/      Fatoora push, PDF streaming
    services/
      zoho/            Zoho Books client, auth, per-resource modules (invoices, items, contacts, expenses)
      telegram/        Bot framework + commands/states for the expense-capture flow
      orchestrators/    Multi-step business logic (resolve/create vendor, create expense)
      gemini_services.py, openrouter_services.py
    database/          SQLAlchemy models, schemas, session setup
    middlewares/       Password gate, Zoho token refresh
    utils/             QR decoding, calculations, filters

frontend/
  src/
    components/       Cart table, item search, payment modal, alerts
    context/, providers/   Password, locale (i18n), cart state
    translations.ts    English / Arabic / Amharic strings
```

## Running locally

**Backend**
```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```
Requires a `.env` with Zoho OAuth credentials, a Postgres connection string, `PASSWORD`, and API keys for Telegram/Gemini/OpenRouter — see `backend/app/core/config.py` for the full list.

**Frontend**
```
cd frontend
npm install
npm run dev
```
Requires `VITE_API_URL` pointing at the backend.

## Known gaps

- The expense/vendor backend logic is fully built but has **no HTTP route** — it's only reachable through the Telegram bot today. The password middleware already exempts `/expenses` and `/vendors`, suggesting this was the plan.
- Zoho-org-specific IDs (tax rate, walk-in customer, invoice template, expense accounts) are hardcoded across a few files rather than centrally configured.
- No automated tests yet.