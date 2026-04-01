
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import  and_, select
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

@router.get('/category/{expense_category}', response_model=list[expense_schema.ExpenseResponse])
def get_expense_by_category(
        expense_category: expense_model.ExpenseCategoryEnum,
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

@router.get('/date/{expense_date}', response_model=list[expense_schema.ExpenseResponse])
def get_expense_by_date(
        expense_date: date,
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
    