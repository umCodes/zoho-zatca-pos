from pydantic import BaseModel

class ContactBase(BaseModel):
    contact_id: str
    tax_reg_no: str
    contact_name: str

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: int
    class Config:
        from_attributes = True
