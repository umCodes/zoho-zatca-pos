from app.services.telegram.setup import telegram
from app.utils.qr_decoder import decode_qr_code 
from app.services.telegram.utils.check_lang import check_language 

from app.services.gemini_services import process_img
import json
import base64


@telegram.command("photo")
async def photo(update, user):
    print("- Obeying Photo Command...")
    try:
        chat_id = update["message"]["chat"]["id"]
        photo = update["message"]["photo"]


        # check if language is missing
        is_language_missing = await check_language("photo", chat_id, user, update)
        if is_language_missing:
            return        
        
        # check if photo is missing
        if not photo:
            return await telegram.send_message(chat_id=chat_id, text=(
                "ፎቶ አልተገኘም። ❌" if user.get("language") == "am"
                else "\u200F" + "الصورة غير صالحة. ❌"
            ))

        if user.get("language") == "am":
            text = (
                "** 🧾 ለሙሉ ደረሰኝ ፎቶ /full_ai_scan ይጫኑ\n\n"
                "** #️⃣ ለQR ኮድ ፎቶ /qrcode ይጫኑ\n\n"
                "⚠️ የሚላኩት የደረሰኝ ፎቶዎች ግልስፅ መሆን አለባቸው።"
            )
        else:
            text = (
                "\u200F" 
                "اضغط /full_ai_scan لمعاينة الفاتورة الكاملة\n\n"
                "اضغط /qrcode لمعاينة صورة رمز qr\n\n"
                "يجب ان تكون الصورة واضحة وعالية الجودة⚠️"
            )
        await telegram.send_message(chat_id=chat_id, text=text)

        user["prev_update"] = update
    except Exception as e:
        print(e)




@telegram.command("/full_ai_scan")
async def full_ai_scan(update, user):
    try:
        chat_id = update["message"]["chat"]["id"]
        photo = user["prev_update"]["message"]["photo"]
        
        file_id = photo[-1]["file_id"]
        file = await telegram.download_file(file_id)
        base64_img = base64.b64encode(file).decode("utf-8")

        data = await process_img(base64_img)

        if "contact_name" not in data:
            await telegram.send_message(chat_id=chat_id, text=(
                "ስህተት ተፈጥሯል። እባክዎ እንደገና ይሞክሩ። ❌" if user.get("language") == "am"
                else "\u200F" + "حدث خطأ أثناء معالجة الصورة. ❌"
            ))
            return
        
        if len(data["tax_reg_no"]) != 15:
            await telegram.send_message(chat_id=chat_id, text=(
                "ፎቶው ግልጽ አደለም። ❌" if user.get("language") == "am"
                else "\u200F" + "الصورة غير واضحة. ❌"
            ))
            return
        
        if user.get("language") == "am":
            text = (
                "📄 የደረሰኝ መረጃ\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"#️⃣ የደረሰኝ ቁጥር: {data['reference_number']}\n"
                f"🏪 አቅራቢ፡ {data['contact_name']}\n"
                f"🧾 VAT: {data['tax_reg_no']}\n"
                f"📅 ታሪክ: {data['date'].split('T')[0]}\n"
                f"💰 ጠቅል ድምር: SAR {data['amount']}"
            )
        else:
            text = (
                "\u200F" +
                "📄 معلومات الفاتورة\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"#️⃣ الفاتورة رقم: {data['reference_number']}\n"
                f"🏪 البائع: {data['contact_name']}\n"
                f"🧾 الرقم الضريبي: {data['tax_reg_no']}\n"
                f"📅 التاريخ: {data['date'].split('T')[0]}\n"
                f"💰 الإجمالي: SAR {data['amount']}"
            )

        await telegram.send_message(chat_id=chat_id, text=text)
        await telegram.send_message(
            chat_id=chat_id,
            text=(
                "ለማረጋገጥ ✅ /ok ይጫኑ\n\nለመተው ❌ /cancel ይጫኑ"
                if user.get("language") == "am"
                else "\u200F" + "للتأكيد ✅ اضغط /ok\n\nللإلغاء ❌ اضغط /cancel"
            )
        )
        user["last_data"] = data
    except Exception as e:
        await telegram.send_message(chat_id=chat_id, text=(
            "ስህተት ተፈጥሯል። እንደገና ይሞክሩ። ❌" if user.get("language") == "am"
            else "\u200F" + "حدث خطأ أثناء معالجة الصورة. ❌"
        ))
        print("Except: ", e)
        return

@telegram.command("/qrcode")
async def qrcode(update, user):
    try:
        chat_id = update["message"]["chat"]["id"]
        photo = user["prev_update"]["message"]["photo"]
        
        # download and decode qr photo
        file_id = photo[-1]["file_id"]
        file = await telegram.download_file(file_id)
        data = decode_qr_code(file).get("data", None)

        # if qr is invalid, return error
        if not data:
            await telegram.send_message(chat_id=chat_id, text=(
                "የQR ኮዱ ልክ አይደለም። ❌" if user.get("language") == "am"
                else "\u200F" + "رمز QR غير صالح. ❌"
            ))
            return
        
        
        if user.get("language") == "am":
            text = (
                "📄 የደረሰኝ መረጃ\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏪 አቅራቢ፡ {data['contact_name']}\n"
                f"🧾 VAT: {data['tax_reg_no']}\n"
                f"📅 ታሪክ: {data['date'].split('T')[0]}\n"
                f"💰 ጠቅል ድምር: SAR {data['amount']}"
            )
        else:
            text = (
                "\u200F" +
                "📄 معلومات الفاتورة\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏪 البائع: {data['contact_name']}\n"
                f"🧾 الرقم الضريبي: {data['tax_reg_no']}\n"
                f"📅 التاريخ: {data['date'].split('T')[0]}\n"
                f"💰 الإجمالي: SAR {data['amount']}"
            )

        await telegram.send_message(chat_id=chat_id, text=text)
        
        await telegram.send_message(
            chat_id=chat_id,
            text=(
                "ለማረጋገጥ ✅ /ok ይጫኑ\n\nለመተው ❌ /cancel ይጫኑ"
                if user.get("language") == "am"
                else "\u200F" + "للتأكيد ✅ اضغط /ok\n\nللإلغاء ❌ اضغط /cancel"
            )
        )
        user["last_data"] = data 
    except Exception as e:
        await telegram.send_message(chat_id=chat_id, text=(
            "ስህተት ተፈጥሯል። እንደገና ይሞክሩ። ❌" if user.get("language") == "am"
            else "\u200F" + "حدث خطأ أثناء معالجة الصورة. ❌"
        ))
        print("Except: ", e)
        return




@telegram.command("/ok")
async def ok(update, user):
    chat_id = update["message"]["chat"]["id"]
    data = user.get("last_data")

    is_language_missing = await check_language("/ok", chat_id, user, update)
    if is_language_missing:
        return        

    if "reference_number" in data:  
        state = telegram.states["confirm_entry"]
        await state(update, user)
        return
    
    user["state"] = "confirm_entry"

    if not data:
        await telegram.send_message(chat_id=chat_id, text=(
            "ምንም መረጃ አልተገኘም። ❌" if user.get("language") == "am"
            else "\u200F" + "لم يتم العثور على بيانات. ❌"
        ))
        return
    
    await telegram.send_message(chat_id=chat_id, text=(
        "የደረሰኝ ቁጥር ያስገቡ: ..." if user.get("language") == "am"
        else "\u200F" + "ادخل رقم الفاتورة: ..."
    ))


@telegram.command("/cancel")
async def cancel(update, user):
    chat_id = update["message"]["chat"]["id"]
    user["last_data"] = None 

    is_language_missing = await check_language("/cancel", chat_id, user, update)
    if is_language_missing:
        return        

    await telegram.send_message(chat_id=chat_id, text=(
        "ደረሰኙ ከምግባት ቀርቷል።" if user.get("language") == "am"
        else "\u200F" + "تم الغاء ادخال الفاتورة"
    ))