from sqlalchemy import Integer, String, Numeric, ForeignKey, CheckConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from datetime import date  



class Contact(Base):
    __tablename__ = "contacts"

    __table_args__ = (
        CheckConstraint("contact_type IN ('customer','vendor')", name="check_customer_type_value"),
    )

    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    contact_type: Mapped[str] = mapped_column(String(9), nullable=False)
    contact_id: Mapped[str] = mapped_column(String(100),unique=True, index=True)
    tax_reg_no: Mapped[str] = mapped_column(String(15), unique=True, index=True)
    contact_name: Mapped[str] = mapped_column(String(100))
    expenses: Mapped[list["Expense"]] = relationship("Expense", back_populates="vendor")


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    reference_number: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    tax_reg_no: Mapped[str] = mapped_column(String(15), index=True)
    expense_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    vendor_id: Mapped[str] = mapped_column(String(100), ForeignKey("contacts.contact_id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    vendor: Mapped["Contact"] = relationship("Contact", back_populates="expenses")


