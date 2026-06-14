from pydantic import BaseModel
from typing import Optional, Literal

class LineItem(BaseModel):
    item_id: str
    rate: Optional[float] = None
    quantity: Optional[float] = None
    tax_percentage: Optional[float] = 15.0
    tax_id:  Literal["46324000000043661"] = "46324000000043661"
    tax_name: Literal["Standard Rate"] = "Standard Rate"


class Invoice(BaseModel):
    customer_id: str
    date: Optional[str] = None
    place_of_supply: Optional[str] = None
    tax_treatment: Optional[str] = None
    billing_address_id: Optional[str] = None
    shipping_address_id: Optional[str] = None
    line_items: list[LineItem]
    notes: Optional[str] = None
    terms: Optional[str] = None
    template_id: Optional[str] = None
    payment_form: Optional[str] = None