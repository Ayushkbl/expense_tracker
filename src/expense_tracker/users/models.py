from pydantic import BaseModel, EmailStr
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from pydantic import BaseModel
from typing import Optional

from expense_tracker.db import Model
from expense_tracker.expense.models import Expense

class User(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    username: Mapped[str]
    email: Mapped[EmailStr] = mapped_column(String(325))
    password_hash: Mapped[str]
    created_at: Mapped[datetime]
    expenses: Mapped[list['Expense']] = relationship(back_populates='user')

    def __repr__(self):
        return f'User(id={self.id}, name={self.name}, email={self.email})'

class UserRequest(BaseModel):
    name: str
    username: str
    email: EmailStr

class UserCreate(UserRequest):
    password_hash: str

class UserResponse(UserRequest):
    id: int
    created_at: datetime
    expenses: Optional[list[Expense]]



