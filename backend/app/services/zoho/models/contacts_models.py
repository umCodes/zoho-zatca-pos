from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator

class CreateContactZoho(BaseModel):
    contact_type: Literal["vendor", "customer"]
    contact_name: str = Field(..., min_length=1)
    company_name: Optional[str] = None
    tax_treatment: Literal["vat_registered", "vat_not_registered"] = "vat_not_registered"
    tax_reg_no: Optional[str] = None
    country_code: str = "SA"

    @model_validator(mode="after")
    def set_defaults_and_validate(self) -> "CreateContactZoho":
        if not self.company_name:
            self.company_name = self.contact_name
        if self.tax_treatment == "vat_registered" and not self.tax_reg_no:
            raise ValueError("tax_reg_no is required when tax_treatment is 'vat_registered'")
        return self
