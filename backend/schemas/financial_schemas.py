from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from enum import Enum

class ExpenseCategory(str, Enum):
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    SECURITY = "security"
    CLEANING = "cleaning"
    ADMIN = "administration"
    OTHER = "other"

class ExpenseBase(BaseModel):
    category: ExpenseCategory
    amount: float
    description: str
    vendor_id: Optional[int] = None
    created_by: str
    status: Optional[str] = "pending"

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True

class VendorBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = 0.0

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int
    expenses: List[Expense] = []

    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    year: int
    month: int
    category: ExpenseCategory
    allocated_amount: float
    actual_amount: Optional[float] = 0.0
    created_by: str
    notes: Optional[str] = None

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    expenses: List[Expense] = []

    class Config:
        from_attributes = True

class ReportSectionBase(BaseModel):
    title: str
    content: str
    chart_data: Optional[str] = None

class ReportSectionCreate(ReportSectionBase):
    pass

class ReportSection(ReportSectionBase):
    id: int
    report_id: int

    class Config:
        from_attributes = True

class FinancialReportBase(BaseModel):
    title: str
    period_start: datetime
    period_end: datetime
    generated_by: str
    status: Optional[str] = "draft"

class FinancialReportCreate(FinancialReportBase):
    sections: List[ReportSectionCreate] = []

class FinancialReport(FinancialReportBase):
    id: int
    generated_at: datetime
    sections: List[ReportSection] = []

    class Config:
        from_attributes = True
