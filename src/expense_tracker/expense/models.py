from decimal import Decimal
from enum import Enum
from datetime import datetime, date
from pytz import timezone
from typing import Optional

from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import Numeric, String, ForeignKey
from sqlalchemy import Enum as SqlEnum

from expense_tracker.db import Model
from expense_tracker.expense import schemas as expense_schemas


class Expense(Model):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), index=True)
    category: Mapped[expense_schemas.ExpenseCategoryEnum] = mapped_column(SqlEnum(expense_schemas.ExpenseCategoryEnum), index=True)
    description: Mapped[str | None] = mapped_column(String(320), default=None, nullable=True)
    expense_date: Mapped[date] = mapped_column(index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d  %H:%M:%S'),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='expenses')

    def __repr__(self):
        return f'Expense(id={self.id}, category={self.category}, amount={self.amount})'

