from app.db.models import Contact
from sqlalchemy.orm import Session
from app.db.schemas import ContactCreate
from app.services.zoho_client import zoho_get

def create_contact(db: Session, contact: ContactCreate):
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts(db: Session):
    return db.query(Contact)


