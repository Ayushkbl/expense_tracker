from enum import Enum
from datetime import datetime
from pytz import timezone
from typing import Optional

from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String, ForeignKey, FLOAT
from sqlalchemy import Enum as SqlEnum

from expense_tracker.db import Model

class ExpenseCategoryEnum(str, Enum):
    groceries = "Groceries"
    leisure = "Leisure"
    food = "Food"
    electronics = "Electronics"
    utilities = "Utilities"
    clothing = "Clothing"
    health = "Health"
    others = "Others"

class Expense(Model):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(FLOAT(precision=2), index=True)
    category: Mapped[ExpenseCategoryEnum] = mapped_column(SqlEnum(ExpenseCategoryEnum), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    expense_date: Mapped[datetime]
    created_at: Mapped[Optional[datetime]] = mapped_column(default=datetime.now(timezone("Asia/Kolkata")), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='expenses')

    def __repr__(self):
        return f'Expense(id={self.id}, category={self.category}, amount={self.amount})'

