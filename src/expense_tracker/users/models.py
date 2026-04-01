from datetime import datetime
from pydantic import EmailStr
from pytz import timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, func

from expense_tracker.db import Model

class User(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(default=None)
    username: Mapped[str] = mapped_column(String(200), index=True, unique=True)
    email: Mapped[EmailStr] = mapped_column(String(325), index=True, unique=True)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
            default=lambda: datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d  %H:%M:%S'),
            nullable=False
    )
    expenses: Mapped[list['Expense']] = relationship(back_populates='user', cascade="all, delete-orphan")
    is_superuser: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f'User(id={self.id}, name={self.name}, email={self.email})'





