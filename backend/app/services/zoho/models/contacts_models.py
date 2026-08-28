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


class CreateCustomerZoho(BaseModel):
    """Same shape as CreateContactZoho, with contact_type locked to 'customer'."""

    contact_type: Literal["customer"] = "customer"
    contact_name: str = Field(..., min_length=1)
    company_name: Optional[str] = None
    tax_treatment: Literal["vat_registered", "vat_not_registered"] = "vat_not_registered"
    tax_reg_no: Optional[str] = None
    country_code: str = "SA"

    @model_validator(mode="after")
    def set_defaults_and_validate(self) -> "CreateCustomerZoho":
        if not self.company_name:
            self.company_name = self.contact_name
        if self.tax_treatment == "vat_registered" and not self.tax_reg_no:
            raise ValueError("tax_reg_no is required when tax_treatment is 'vat_registered'")
        return self


class CustomerAddress(BaseModel):
    """Maps onto Zoho's billing_address / shipping_address object.
    building_number / additional_number / zip are digit strings — identical
    in both languages, so the API accepts a single value and mirrors it onto
    both the primary and _sec_lang Zoho fields. street/district/city/state/
    country are real text that differs by language and keep separate
    primary + _sec_lang fields (verified against a live contact record)."""

    building_number: Optional[str] = None
    street: Optional[str] = None                      # Zoho: street2
    street_sec_lang: Optional[str] = None
    additional_number: Optional[str] = None
    district: Optional[str] = None
    district_sec_lang: Optional[str] = None
    city: Optional[str] = None
    city_sec_lang: Optional[str] = None
    state: Optional[str] = None
    state_sec_lang: Optional[str] = None
    zip: Optional[str] = None                          # postal code
    country: Optional[str] = None
    country_sec_lang: Optional[str] = None

    def to_zoho(self, country_code: str = "SA", phone: Optional[str] = None) -> dict:
        fields = {
            "address": self.building_number,
            "address_sec_lang": self.building_number,
            "street2": self.street,
            "street2_sec_lang": self.street_sec_lang,
            "additional_number": self.additional_number,
            "additional_number_sec_lang": self.additional_number,
            "district": self.district,
            "district_sec_lang": self.district_sec_lang,
            "city": self.city,
            "city_sec_lang": self.city_sec_lang,
            "state": self.state,
            "state_sec_lang": self.state_sec_lang,
            "zip": self.zip,
            "zip_sec_lang": self.zip,
            "country": self.country,
            "country_sec_lang": self.country_sec_lang,
            "country_code": country_code,
            "phone": phone,
        }
        return {k: v for k, v in fields.items() if v is not None}


class CreateCustomerDetailedZoho(BaseModel):
    """Full bilingual customer-creation model for the create-customer modal.
    Primary name/address fields are Arabic (per business convention), with an
    English (sec_lang) counterpart — mirroring how Zoho itself stores real
    KSA contacts (verified against a live record). VAT and CRN are required;
    this business only ever identifies customers by CRN, so buyer_id_label
    is fixed rather than user-selectable."""

    contact_type: Literal["customer"] = "customer"

    contact_name: str = Field(..., min_length=1)               # Arabic — primary
    contact_name_sec_lang: str = Field(..., min_length=1)       # English — secondary

    # Zoho has no top-level contact phone field for create — it only persists
    # via billing_address.phone (verified against the live API), so this is
    # folded into billing_address when building the Zoho payload.
    phone: Optional[str] = None

    tax_treatment: Literal["vat_registered"] = "vat_registered"
    tax_reg_no: str = Field(..., min_length=1)                   # VAT / TRN — required

    buyer_id_value: str = Field(..., min_length=1)               # CRN — required

    billing_address: CustomerAddress

    country_code: str = "SA"

    @property
    def buyer_id_label(self) -> str:
        return "CRN"
