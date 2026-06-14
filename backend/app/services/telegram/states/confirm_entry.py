from app.services.telegram.setup import telegram
import json
from app.services.orchestrators.expenses_services import create_expense
from app.services.zoho.models.expenses_models import CreateExpenseZoho

@telegram.state("confirm_entry")
async def confirm_entry(update, user):
    print("Applying Confirm Entry State...")
    try:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]
    except (KeyError, TypeError) as e:
        print("Confirm Entry Error: ", e)
        return

    is_amharic = user.get("language") == "am"
    qr = user.get("last_qr")
    user["state"] = None

    if not qr:
        await telegram.send_message(chat_id=chat_id, text="No QR data found.")
        return

    for key in telegram.commands.keys():
        if text.startswith(key):
            await telegram.send_message(chat_id=chat_id, text="Invalid Purchase Invoice Id")
            return

    try:
        expense = await create_expense(expense=CreateExpenseZoho(
            tax_reg_no=qr["vat_number"],
            contact_name=qr["seller"],
            amount=qr["total"],
            reference_number=text,
            date=qr["timestamp"].split("T")[0]
        ))
        if expense["error"] == "Expense already exists" or expense["error"] == "Expense already exists":
            await telegram.send_message(chat_id=chat_id, text=(
                "ℹ️ የግዢ ደረሰኝ ከሁን በፊት ገብቷል።" if is_amharic else "ℹ️ الفاتورة موجودة مسبقاً"
            ))
            return
        

    except Exception:
        await telegram.send_message(chat_id=chat_id, text=(
            "ሂደቱ ተቋርጧል ❌" if is_amharic else "فشلت العملية ❌"
        ))
        return
    finally:
        user["last_qr"] = None

    if not expense.get("ok"):
        await telegram.send_message(chat_id=chat_id, text=(
            "ሂደቱ ተቋርጧል ❌" if is_amharic else "فشلت العملية ❌"
        ))
        return

    await telegram.send_message(chat_id=chat_id, text=(
        f"የግዥ ደረሰኝ ቁጥር {text} በትክክል ገብቷል ✅"
        if is_amharic else
        "\u200F" + f"تم انشاء فاتورة المشتريات رقم {text} بنجاح ✅"
    ))

