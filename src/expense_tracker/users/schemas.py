from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr, Field
from typing import Optional

from expense_tracker.expense import schemas as expense_schema

class UserBase(BaseModel):
    name: str | None = None
    username: str = Field(max_length=200)
    email: EmailStr = Field(max_length=325)
    is_superuser: bool = Field(default=False)

class UserCreate(UserBase):
    password: SecretStr

class UserUpdate(BaseModel):
    name: str | None = None
    username: str | None = Field(default=None, max_length=200)
    email: EmailStr | None = Field(default=None, max_length=325)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    created_at: datetime | None
    expenses: list[expense_schema.ExpenseResponse] | None

class UserPasswordUpdate(BaseModel):
    old_password: SecretStr
    new_password: SecretStr
    verify_new_password: SecretStr