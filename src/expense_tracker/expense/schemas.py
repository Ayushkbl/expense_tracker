from enum import Enum
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ExpenseCategoryEnum(str, Enum):
    groceries = "Groceries"
    leisure = "Leisure"
    food = "Food"
    electronics = "Electronics"
    utilities = "Utilities"
    clothing = "Clothing"
    health = "Health"
    others = "Others"

class ExpenseFilter(str, Enum):
    past_week = "Past Week"
    past_month = "Past Month"
    last_3_months = "Last 3 months"
    past_year = "Past Year"

class ExpenseBase(BaseModel):
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    category: ExpenseCategoryEnum
    description: str | None = Field(default=None, max_length=320)
    expense_date: date

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None
    user_id: int

class ExpenseUpdate(BaseModel):
    amount: Decimal | None = Field(max_digits=10, default=None, decimal_places=2)
    category: ExpenseCategoryEnum | None = Field(default=None)
    description: str | None = Field(default=None, max_length=320)
    expense_date: date | None = Field(default=None)

class ExpenseCategories(BaseModel):
    groceries: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    leisure: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    food: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    electronics: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    utilities: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    clothing: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    health: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    others: Decimal = Field(default=0, max_digits=10, decimal_places=2)

class ExpenseSummary(BaseModel):
    total_amount: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    category_breakdown: ExpenseCategories


class SummaryDetails(BaseModel):
    expense_summary: ExpenseSummary
    all_expenses: list[ExpenseResponse]
    filter_applied: ExpenseFilter | None = Field(default=None)
    total_expenses: int
