import base64
import cv2
import numpy as np
import base64
from pyzbar.pyzbar import decode
import zxingcpp



def extract_info(qr_string: str) -> dict:
    data = base64.b64decode(qr_string)
    print(data)
    i = 0
    result = {}

    while i < len(data):
        tag = data[i]
        length = data[i + 1]
        value_bytes = data[i + 2 : i + 2 + length]

        try:
            value = value_bytes.decode("utf-8")
        except UnicodeDecodeError:
            value = value_bytes

        if tag == 1:
            result["seller"] = value
        elif tag == 2:
            result["vat_number"] = value
        elif tag == 3:
            result["timestamp"] = value
        elif tag == 4:
            result["total"] = float(value)
        elif tag == 5:
            result["vat_amount"] = float(value)
        elif tag == 6:
            result["signature"] = value_bytes
        else:
            result[f"tag_{tag}"] = value

        i += 2 + length

    return result




def decode_qr_code(b64_string: str):

    if "," in b64_string:
        b64_string = b64_string.split(",")[1]

    # decode base64 → bytes
    img_bytes = base64.b64decode(b64_string)

    # convert bytes → numpy array
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)

    # decode image
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    results = zxingcpp.read_barcodes(img)
    for r in results:
        print(r.text)
        if r.text:
            return {
                "data": extract_info(r.text)
            }
    return { "data": None }
