from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Enum for expense categories
class ExpenseCategory(str, Enum):
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    SECURITY = "security"
    CLEANING = "cleaning"
    ADMIN = "administration"
    OTHER = "other"

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(Enum(ExpenseCategory), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    created_by = Column(String, nullable=False)
    status = Column(String, default="pending")
    
    vendor = relationship("Vendor", back_populates="expenses")

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_person = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    rating = Column(Float, default=0.0)
    
    expenses = relationship("Expense", back_populates="vendor")

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    category = Column(Enum(ExpenseCategory), nullable=False)
    allocated_amount = Column(Float, nullable=False)
    actual_amount = Column(Float, default=0.0)
    created_by = Column(String, nullable=False)
    notes = Column(String)
    
    expenses = relationship("Expense", back_populates="budget")

class FinancialReport(Base):
    __tablename__ = "financial_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    generated_by = Column(String, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="draft")
    
    sections = relationship("ReportSection", back_populates="report")

class ReportSection(Base):
    __tablename__ = "report_sections"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("financial_reports.id"))
    title = Column(String, nullable=False)
    content = Column(String)
    chart_data = Column(String)
    
    report = relationship("FinancialReport", back_populates="sections")
