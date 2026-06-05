from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base



class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    contact_id: Mapped[str] = mapped_column(String(100),unique=True, index=True)
    tax_reg_no: Mapped[str] = mapped_column(String(15), unique=True, index=True)
    contact_name: Mapped[str] = mapped_column(String(100))