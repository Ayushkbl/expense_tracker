from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from expense_tracker.expense import models as expense_model

class ExpenseBase(BaseModel):
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    category: expense_model.ExpenseCategoryEnum
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
    amount: Decimal | None = Field(default=None, decimal_places=2)
    category: expense_model.ExpenseCategoryEnum | None = Field(default=None)
    description: str | None = Field(default=None, max_length=320)
    expense_date: date | None = Field(default=None)

