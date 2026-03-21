from enum import Enum
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String, ForeignKey
from datetime import datetime
from sqlalchemy.sql import func
from typing import Optional

from expense_tracker.db import Model
from expense_tracker.users.models import User

class Expense(Model):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float]
    category: Mapped['ExpenseCategoryEnum']
    description: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    expense_date: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='expenses')

    def __repr__(self):
        return f'Expense(id={self.id}, category={self.category}, amount={self.amount})'

class ExpenseCategoryEnum(str, Enum):
    groceries = "Groceries"
    leisure = "Leisure"
    food = "Food"
    electronics = "Electronics"
    utilities = "Utilities"
    clothing = "Clothing"
    health = "Health"
    others = "Others"

