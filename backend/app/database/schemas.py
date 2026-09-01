from pydantic import BaseModel
from typing import Optional, Literal
from datetime import date as date_type


# Validation Schema

# ─── Contact Schemas ───────────────────────────────────────

class ContactBase(BaseModel):
    contact_id: str
    contact_type: Literal["vendor", "customer"]
    tax_reg_no: str
    contact_name: str

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True


# ─── Expense Schemas ───────────────────────────────────────

class ExpenseBase(BaseModel):
    expense_id: str
    tax_reg_no: str
    amount: float
    reference_number: str
    date: str
    vendor_id: str

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    date: date_type  # Expense.date is a SQL Date column, not a string
    vendor: Optional[ContactResponse] = None  # nested contact object

    class Config:
        from_attributes = True