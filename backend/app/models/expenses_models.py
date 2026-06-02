# models/expenses.py
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator

class ExpenseModel(BaseModel):
    account_id: str = "46324000000000443"
    date: str
    amount: Decimal = Field(..., gt=0)
    paid_through_account_id: str = "46324000000000323"
    vendor_id: Optional[str] = None
    reference_number: str
    
    tax_treatment: Literal["vat_registered", "vat_not_registered"] = "vat_not_registered"
    tax_id: Optional[str] = "46324000000043661"
    # tax_percentage: Optional[Literal[15]] = None
    tax_reg_no: Optional[str] = None
    place_of_supply: str = "SA"
    is_inclusive_tax: Optional[bool] = True

    @model_validator(mode="after")
    def set_vat_fields(self) -> "ExpenseModel":
        if self.tax_treatment == "vat_registered":
            if not self.tax_reg_no:
                raise ValueError("tax_reg_no is required when tax_treatment is 'vat_registered'")
            # self.tax_percentage = 15
            self.tax_id = "46324000000043661"
        return self