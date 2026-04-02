
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import  and_, func, select
from sqlalchemy.orm import Session

from expense_tracker.auth import CurrentUser
from expense_tracker.db import get_db
from expense_tracker.expense import schemas as expense_schema
from expense_tracker.expense import models as expense_model

router = APIRouter()

@router.get('', response_model=list[expense_schema.ExpenseResponse])
def get_all_expenses(
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)]
):
    
    expenses = db.scalars(
        select(expense_model.Expense)
        .where(expense_model.Expense.user_id == current_user.id)
    ).all()

    if not expenses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no Expenses created for you. Please create an expense first"
        )
    
    return expenses

@router.get('/id/{expense_id}', response_model=expense_schema.ExpenseResponse)
def get_expense_by_id(
        expense_id: int,
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)]
):
    
    expense = db.scalar(
        select(expense_model.Expense)
        .where(and_(
            expense_model.Expense.user_id == current_user.id,
            expense_model.Expense.id == expense_id
        ))
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no expenses with expense id = {expense_id}"
        )
    
    return expense

@router.get('/category', response_model=list[expense_schema.ExpenseResponse])
def get_expense_by_category(
        expense_category: Annotated[expense_schema.ExpenseCategoryEnum, Query()],
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)]
):
    
    expenses = db.scalars(
        select(expense_model.Expense)
        .where(and_(
            expense_model.Expense.user_id == current_user.id,
            expense_model.Expense.category == expense_category.value
        ))
    ).all()

    if not expenses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no expenses with expense category = {expense_category.value}"
        )
    
    return expenses

@router.get('/date', response_model=list[expense_schema.ExpenseResponse])
def get_expense_by_date(
        expense_date: Annotated[date, Query()],
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)]
):
    
    expenses = db.scalars(
        select(expense_model.Expense)
        .where(and_(
            expense_model.Expense.user_id == current_user.id,
            expense_model.Expense.expense_date == expense_date
        ))
    ).all()

    if not expenses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no expenses with date = {expense_date}"
        )
    
    return expenses

@router.get('/summary', response_model=expense_schema.SummaryDetails)
def get_expense_summary(
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)],
        expense_filter: Annotated[expense_schema.ExpenseFilter | None, Query()] = None
):

    base_query = select(expense_model.Expense).where(expense_model.Expense.user_id == current_user.id)
    today = datetime.now(timezone("Asia/Kolkata")).date()

    match expense_filter:
        case expense_schema.ExpenseFilter.past_week:
            start_date = today - relativedelta(weeks=1)
        case expense_schema.ExpenseFilter.past_month:
            start_date = today - relativedelta(month=1)
        case expense_schema.ExpenseFilter.last_3_months:
            start_date = today - relativedelta(months=3)
        case expense_schema.ExpenseFilter.past_year:
            start_date = today - relativedelta(years=1)
        case _:
            start_date = None
    
    if start_date:
        base_query = base_query.where(expense_model.Expense.expense_date >= start_date)
    
    total_amount = db.scalar(
        select(func.sum(expense_model.Expense.amount))
        .where(and_(
            expense_model.Expense.user_id == current_user.id,
            expense_model.Expense.expense_date >= start_date if start_date else True
        ))
    )

    category_result = db.execute(
        select(func.sum(expense_model.Expense.amount),expense_model.Expense.category)
        .where(and_(
            expense_model.Expense.user_id == current_user.id,
            expense_model.Expense.expense_date >= start_date if start_date else True
        ))
        .group_by(expense_model.Expense.category)
    ).all()

    category_breakdown = expense_schema.ExpenseCategories()
    for amount, category in category_result:
        category_name = category.value.lower()
        setattr(category_breakdown, category_name, amount)
    
    expenses = db.scalars(base_query).all()
    expense_summary = expense_schema.ExpenseSummary(
        total_amount=total_amount,
        category_breakdown=category_breakdown
    )

    return expense_schema.SummaryDetails(
       expense_summary=expense_summary,
       all_expenses=expenses,
       filter_applied=expense_filter.value if expense_filter else None,
       total_expenses=len(expenses)
    )


@router.post('', response_model=expense_schema.ExpenseResponse)
def create_expense(
        new_expense: Annotated[expense_schema.ExpenseCreate, Query()],
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)]
):

    expense = expense_model.Expense(
        amount = new_expense.amount,
        category = new_expense.category,
        description = new_expense.description,
        expense_date = new_expense.expense_date,
        user_id = current_user.id
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense

@router.patch('/update/{expense_id}', response_model=expense_schema.ExpenseResponse)
def update_expense(
        expense_id: int,
        expense_update: Annotated[expense_schema.ExpenseUpdate, Query()],
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)]
):

    expense = db.scalar(
        select(expense_model.Expense)
        .where(and_(
            expense_model.Expense.user_id == current_user.id,
            expense_model.Expense.id == expense_id
        ))
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Please enter an existing expense id"
        )

    update_dict = expense_update.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(expense, key, value)
    
    db.commit()
    db.refresh(expense)

    return expense


@router.delete('/delete/{expense_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
        expense_id: int,
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)]
):

    expense = db.scalar(
        select(expense_model.Expense)
        .where(and_(
            expense_model.Expense.user_id == current_user.id,
            expense_model.Expense.id == expense_id
        ))
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no expenses with expense id = {expense_id}"
        )
    
    db.delete(expense)
    db.commit()
    