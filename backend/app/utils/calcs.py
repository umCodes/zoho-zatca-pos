# calcs.py

def extract_vat(item: dict) -> float:
    if item.get("tax_percentage") == 15:
        return item["rate"]
    vat = 1.15
    return round(item["rate"] / vat, 2)

