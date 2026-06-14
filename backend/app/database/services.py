from app.database.models import Contact, Expense
from sqlalchemy.orm import Session
from app.database.schemas import ContactCreate, ExpenseCreate
from app.services.zoho.modules.contacts import get_contacts, get_contact


def create_contact_db(db: Session, contact: ContactCreate):
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts_db(db: Session):
    contacts = db.query(Contact).all()
    return [contact.__dict__ for contact in contacts]

def get_contact_by_id_db(db: Session, contact_id: str):
    return db.query(Contact).filter(Contact.contact_id == contact_id).first()


def get_contact_by_tax_reg_no_db(db: Session, tax_reg_no: str):
    return db.query(Contact).filter(Contact.tax_reg_no == tax_reg_no).first()


def delete_contact_db(db: Session, contact_id: str):
    db_contact = db.query(Contact).filter(Contact.contact_id == contact_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact




async def migrate_all_vendors_from_zoho(db: Session):
    vendors = await get_contacts({"contact_type": "vendor" })

    for vendor in vendors["contacts"]:
        exists = get_contact_by_id_db(db=db, contact_id=vendor["contact_id"])

        if exists: continue
        res = await get_contact(vendor["contact_id"])
        vendor = res["contact"]
        res = create_contact_db(db=db, contact=ContactCreate(
            contact_id=vendor["contact_id"],
            contact_type=vendor["contact_type"],
            tax_reg_no=vendor["tax_reg_no"],
            contact_name=vendor["contact_name"]
        ))
    vendors = get_contacts_db(db=db)
    return {"vendors": vendors}


def create_expense_db(db: Session, expense: ExpenseCreate):
    exists = get_expense_by_reference_number_db(db=db, reference_number=expense.reference_number)
    if exists:
        return {"error": "Expense already exists", "source": "db", "expense_id": expense.expense_id}
    
    db_expense = Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses_db(db: Session):
    return db.query(Expense)

def get_expense_db(db: Session, expense_id: str):
    return db.query(Expense).filter(Expense.expense_id == expense_id).first()

def get_expense_by_reference_number_db(db: Session, reference_number: str):
    return db.query(Expense).filter(Expense.reference_number == reference_number).first()

def get_expenses_by_vendor_db(db: Session, vendor_id: str):
    return db.query(Expense).filter(Expense.vendor_id == vendor_id).all()

def delete_expense_db(db: Session, expense_id: str):
    db_expense = db.query(Expense).filter(Expense.expense_id == expense_id).first()
    if db_expense:
        db.delete(db_expense)
        db.commit()
    return db_expense