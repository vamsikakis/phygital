from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import financial_models as models
from ..schemas import financial_schemas as schemas

router = APIRouter(prefix="/api/financial", tags=["Financial Analysis"])

@router.post("/expenses/", response_model=schemas.Expense)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = models.Expense(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.get("/expenses/", response_model=List[schemas.Expense])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).offset(skip).limit(limit).all()
    return expenses

@router.get("/expenses/summary/")
def get_expense_summary(start_date: str, end_date: str, db: Session = Depends(get_db)):
    try:
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
        
        expenses = db.query(models.Expense).filter(
            models.Expense.date >= start_date,
            models.Expense.date <= end_date
        ).all()
        
        summary = {
            "total_amount": sum(exp.amount for exp in expenses),
            "by_category": {},
            "by_vendor": {}
        }
        
        for exp in expenses:
            if exp.category not in summary["by_category"]:
                summary["by_category"][exp.category] = 0
            summary["by_category"][exp.category] += exp.amount
            
            if exp.vendor_id not in summary["by_vendor"]:
                summary["by_vendor"][exp.vendor_id] = 0
            summary["by_vendor"][exp.vendor_id] += exp.amount
            
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/vendors/", response_model=schemas.Vendor)
def create_vendor(vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    db_vendor = models.Vendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

@router.get("/vendors/", response_model=List[schemas.Vendor])
def read_vendors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    vendors = db.query(models.Vendor).offset(skip).limit(limit).all()
    return vendors

@router.get("/budgets/", response_model=List[schemas.Budget])
def read_budgets(year: int = None, month: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Budget)
    if year:
        query = query.filter(models.Budget.year == year)
    if month:
        query = query.filter(models.Budget.month == month)
    return query.all()

@router.post("/reports/", response_model=schemas.FinancialReport)
def create_report(report: schemas.ReportCreate, db: Session = Depends(get_db)):
    db_report = models.FinancialReport(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report
