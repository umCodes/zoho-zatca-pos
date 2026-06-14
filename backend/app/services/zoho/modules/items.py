from app.services.zoho.client import zoho_client
from app.utils.filters import filter_list_fields
ITEM_FIELDS = {
    "item_id",
    "name",
    "status",
    "description",
    "rate",
    "unit",
    "tax_id",
    "tax_name",
    "tax_percentage",
    "sku"
}

ALL_ITEMS = []
async def get_items():
    page = 1
    per_page = 200
    all_items = []

    if len(ALL_ITEMS) > 0:
        return ALL_ITEMS
    
    while True:
        
        if page == 7:
            break

        res = await zoho_client.request(path="/items", params={"page": page, "per_page": per_page})
        data = res.json()
        items = data.get("items", [])

        all_items.extend(items)

    

        page += 1
    all_items = filter_list_fields(all_items, ITEM_FIELDS)
    return all_items