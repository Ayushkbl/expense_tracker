from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from expense_tracker.expense import models as expense_model

class ExpenseBase(BaseModel):
    amount: float = Field(decimal_places=2)
    category: expense_model.ExpenseCategoryEnum
    description: str | None = Field(default=None, max_length=320)
    expense_date: datetime

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None
    user_id: int



