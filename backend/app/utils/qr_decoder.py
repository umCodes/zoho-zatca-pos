import base64
import cv2
import numpy as np
import base64
import zxingcpp



def extract_info(qr_string: str) -> dict:
    data = base64.b64decode(qr_string)
    i = 0
    result = {}

    while i < len(data):
        tag = data[i]
        length = data[i + 1]
        value_bytes = data[i + 2 : i + 2 + length]

        try:
            value = value_bytes.decode("utf-8")
        except UnicodeDecodeError:
            print(" * UnicodeDecodeError")
            value = value_bytes

        if tag == 1:
            result["seller"] = value
        elif tag == 2:
            result["vat_number"] = value
        elif tag == 3:
            result["timestamp"] = value.split(" ")[0]
        elif tag == 4:
            result["total"] = float(value)
        elif tag == 5:
            result["vat_amount"] = float(value)
        elif tag == 6:
            result["signature"] = value_bytes
        else:
            result[f"tag_{tag}"] = value

        i += 2 + length
    if result:
        print(" * Data Extracted from QR Code Result")

    return {
        "contact_name": result.get("seller", ""),
        "tax_reg_no": result.get("vat_number", ""),
        "date": result.get("timestamp", ""),
        "amount": result.get("total", 0)
    }



def decode_qr_code(img_bytes: bytes):
    try:
        print("Decoding QR Photo Bytes...")

        # bytes → numpy array
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)

        # decode image 
        img = cv2.imdecode(img_array, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        if img is None:
            print("Error: Failed to decode image")
            return {"data": None}

        results = zxingcpp.read_barcodes(img, formats=[zxingcpp.BarcodeFormat.QRCode])

        for r in results:
            if r.text:
                print(" * Result Found from QR Code ")
                return {
                    "data": extract_info(r.text)
                }
        return {"data": None}
    except Exception as e:
        print("Error: ", e)
        return {"data": None}