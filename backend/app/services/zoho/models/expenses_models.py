from pydantic import BaseModel, model_validator
from typing import Optional, Literal
import json
class CreateExpenseZoho(BaseModel):

    account_id: Optional[str] = "46324000000000443"
    paid_through_account_id: Optional[str] = "46324000000000323"
    contact_name: Optional[str] = None

    tax_id: Optional[str] = "46324000000043661"
    tax_reg_no: Optional[str] = None
    tax_treatment: Literal["vat_registered", "vat_not_registered"] = "vat_not_registered"
    place_of_supply: str = "SA"
    is_inclusive_tax: Optional[bool] = True

    description: Optional[str] = None
    amount: float
    reference_number: str
    date: str
    vendor_id: Optional[str] = None


    @model_validator(mode="after")
    def set_vat_fields(self) -> "CreateExpenseZoho":
        if self.tax_reg_no:
            self.tax_treatment = "vat_registered"
        if self.tax_treatment == "vat_registered":
            if not self.tax_reg_no:
                raise ValueError(
                    "tax_reg_no is required when tax_treatment is 'vat_registered'"
                )

            self.tax_id = "46324000000043661"
        return self

    def build_description_fingerprint(self) -> str:
        return json.dumps(
            {
                "contact_name": self.contact_name,
                "date": self.date,
                "tax_reg_no": self.tax_reg_no,
                "total": self.amount,
            },

            sort_keys=True,
            ensure_ascii=False
        )

