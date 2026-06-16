from app.services.telegram.setup import telegram
import json
from app.services.orchestrators.expenses_services import create_expense
from app.services.zoho.models.expenses_models import CreateExpenseZoho

@telegram.state("confirm_entry")
async def confirm_entry(update, user):
    print("Applying Confirm Entry State...")
    try:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text") 
    except (KeyError, TypeError) as e:
        print("Confirm Entry Error: ", e)
        return
    is_amharic = user.get("language") == "am"
    data = user.get("last_data")
    user["state"] = None
    if not data:
        await telegram.send_message(chat_id=chat_id, text=(
            "ምንም መረጃ አልተገኘም። ❌" if is_amharic else "\u200F" + "لم يتم العثور على بيانات. ❌"
        ))
        return
    if "reference_number" not in data:
        data["reference_number"] = text
    try:
        expense = await create_expense(expense=CreateExpenseZoho(
            tax_reg_no=data["tax_reg_no"],
            contact_name=data["contact_name"],
            amount=data["amount"],
            reference_number=data["reference_number"],
            date=data["date"].split("T")[0]
        ))
        print("Expense: ", expense)
        error = expense.get("error", "")
        if isinstance(error, str) and error.startswith("Expense already exists"):
            await telegram.send_message(chat_id=chat_id, text=(
                "ℹ️ የግዢ ደረሰኝ ከሁን በፊት ገብቷል።" if is_amharic else "ℹ️ الفاتورة موجودة مسبقاً"
            ))
            return        
        
        if not expense.get("ok"):
            print(" * Expense Not OK: ", expense)
            raise Exception(expense)
        
        await telegram.send_message(chat_id=chat_id, text=(
            f"የግዥ ደረሰኝ ቁጥር {data['reference_number']} በትክክል ገብቷል ✅"
            if is_amharic else
            "\u200F" + f"تم انشاء فاتورة المشتريات رقم {data['reference_number']} بنجاح ✅"
        ))
    except Exception as e:
        print("- Expense Error: ", e)
        await telegram.send_message(chat_id=chat_id, text=(
            "ሂደቱ ተቋርጧል ❌" if is_amharic else "فشلت العملية ❌"
        ))
        return
    finally:
        user["last_data"] = None