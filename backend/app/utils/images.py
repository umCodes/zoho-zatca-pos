import base64
def encode_image_to_base64(image_path: str) -> str: 
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string