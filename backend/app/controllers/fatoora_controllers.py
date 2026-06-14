from app.services.zoho.modules.invoices import get_invoices, push_to_fatoora, mark_invoice_as_sent



async def _push_invoices(from_date: str) -> dict:
    invoices = await get_invoices(
        params={
            "date_start": from_date,
            "sort_column": "invoice_number",
        }
    )
    print(invoices)
    for invoice in reversed(invoices):
        print(f"Processing: {invoice['invoice_number']}")
        try:
            await push_to_fatoora(invoice)
            if invoice["status"] == "draft":
                result = await mark_invoice_as_sent(invoice["invoice_id"])
                print(f"{invoice['invoice_number']}: {result} ⬆️")
        except Exception as err:
            print(f"Failed: {invoice['invoice_number']} — {err}")

    return {"processed": len(invoices)}



# # ---------------------------------------------------------------------------
# # Dev hints
# # ---------------------------------------------------------------------------

# def _print_dev_hints(port: int) -> None:
#     yesterday = (date.today() - timedelta(days=1)).isoformat()
#     cyan   = lambda s: f"\x1b[36m{s}\x1b[0m"
#     yellow = lambda s: f"\x1b[33m{s}\x1b[0m"
#     green  = lambda s: f"\x1b[32m{s}\x1b[0m"

#     print("\nPaste in PowerShell:")
#     print(cyan("$response = Invoke-RestMethod `"))
#     print(yellow(f'  -Uri "http://localhost:{port}/push-invoices?from={yesterday}" `'))
#     print(green("  -Method Get"))
#     print(cyan("$response"))


# if __name__ == "__main__":
#     import uvicorn

#     PORT = 3000
#     _print_dev_hints(PORT)
#     uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)