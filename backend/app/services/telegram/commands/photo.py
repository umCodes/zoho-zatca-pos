from app.services.telegram.setup import telegram
from app.utils.qr_decoder import decode_qr_code 
from app.services.telegram.utils.check_lang import check_language 

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
            return await telegram.send_message(chat_id=chat_id, text="Invalid File")
            
        # download and decode qr photo
        file_id = photo[-1]["file_id"]
        file = await telegram.download_file(file_id)
        qr = decode_qr_code(file)

        # if qr is invalid, return error
        if not qr["data"]:
            await telegram.send_message(chat_id=chat_id, text="Invalid QR Code")
            return
        
        # send qr data to user
        if user.get("language") == "am":
            text = (
                "📄 የደረሰኝ መረጃ\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏪 አቅራቢ፡ {qr["data"]['seller']}\n"
                f"🧾 VAT: {qr["data"]['vat_number']}\n"
                f"📅 ታሪክ: {qr["data"]['timestamp'].split('T')[0]}\n"
                f"💰 ጠቅል ድምር: SAR {qr["data"]['total']}"
            )
        else:
            text = (
                "\u200F" +
                "📄 معلومات الفاتورة\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏪 البائع: {qr["data"]['seller']}\n"
                f"🧾 VAT: {qr["data"]['vat_number']}\n"
                f"📅 التاريخ: {qr["data"]['timestamp'].split('T')[0]}\n"
                f"💰 الإجمالي: SAR {qr["data"]['total']}"
            )

        await telegram.send_message(chat_id=chat_id, text=text)

        await telegram.send_message(
            chat_id=chat_id,
            text=(
                "ለማረጋገጥ ✅ /ok ይጫኑ\n\nለመተው ❌ /cancel ይጫኑ"
                if user.get("language") == "am"
                else "للتأكيد ✅ اضغط /ok\n\nللإلغاء ❌ اضغط /cancel"
            )
        )
        user["last_qr"] = qr["data"]
    except Exception as e:
        print(e)




@telegram.command("/ok")
async def ok(update, user):
    chat_id = update["message"]["chat"]["id"]
    qr = user.get("last_qr")
    user["state"] = "confirm_entry"

    is_language_missing = await check_language("/ok", chat_id, user, update)
    if is_language_missing:
        return        
        

    if not qr:
        await telegram.send_message(chat_id=chat_id, text="No QR data found.")
        return
    
    await telegram.send_message(chat_id=chat_id, text=(
        "የደረሰኝ ቁጥር ያስገቡ: ..." if user.get("language") == "am"
        else "\u200F" + "ادخل رقم الفاتورة: ..."

    ))


@telegram.command("/cancel")
async def cancel(update, user):
    chat_id = update["message"]["chat"]["id"]
    user["last_qr"] =  None 

    is_language_missing = await check_language("/cancel", chat_id, user, update)
    if is_language_missing:
        return        

    await telegram.send_message(chat_id=chat_id, text=(
        "ደረሰኙ ከምግባት ቀርቷል።" if user.get("language") == "am"
        else "تم الغاء ادخال الفاتورة"

    ))
