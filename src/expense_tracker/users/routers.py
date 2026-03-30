from datetime import timedelta, datetime
import email
from typing import Annotated

from alembic.command import current
from fastapi import APIRouter, Depends, Form, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from starlette.status import HTTP_400_BAD_REQUEST

from expense_tracker.db import Session, get_db
from expense_tracker.auth import CurrentUser, Token, create_access_token, hash_password, password_hash, verify_password
from expense_tracker.config import settings
from expense_tracker.users import models as users_model
from expense_tracker.users import schemas as users_schema

router = APIRouter()

@router.get('/me', response_model=users_schema.UserResponse)
def get_loggedin_user(current_user: CurrentUser):
    return current_user


@router.get('', response_model=list[users_schema.UserResponse])
def get_all_users(
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)]
):

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only admins are allowed to fetch other user details"
        )

    all_users = db.scalars(
        select(users_model.User)
        .order_by(users_model.User.username)
    ).all()

    return all_users



@router.post('/token', response_model=Token)
def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[Session, Depends(get_db)]
):
    
    user = db.scalar(
        select(users_model.User)
        .where(users_model.User.username == form_data.username.lower())
    )
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expire_minutes = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.username)},
        expires_delta=access_token_expire_minutes,
    )

    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.post('', response_model=users_schema.UserResponse)
def register_user(
        new_user: users_schema.UserCreate,
        db: Annotated[Session, Depends(get_db)]
):

    chk_user = db.scalar(select(users_model.User).where(users_model.User.username == new_user.username.lower()))
    if chk_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user already exists with the same username"
        )
    
    chk_user = db.scalar(
        select(users_model.User)
        .where(users_model.User.email == new_user.email.lower())
    )
    if chk_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user already exists with the same email"
        )
    
    hashed_password = hash_password(new_user.password.get_secret_value())

    user = users_model.User(
        name=new_user.name,
        username=new_user.username.lower(),
        email=new_user.email.lower(),
        password_hash=hashed_password,
        is_superuser=new_user.is_superuser
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.patch('/password')
def reset_password(
        password_details: users_schema.UserPasswordUpdate,
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)]
):

    if not verify_password(password_details.old_password.get_secret_value(), current_user.password_hash):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="The password entered does not match with the logged in user password"
        )
    
    if verify_password(password_details.new_password.get_secret_value(), current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password should not be same as the current password"
        )

    if password_details.new_password.get_secret_value() != password_details.verify_new_password.get_secret_value():
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Both the new password field does not match"
        )
    
    new_password_hash = hash_password(password_details.new_password.get_secret_value())

    current_user.password_hash = new_password_hash

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Password Updated Successfully!"
    }

@router.patch('/update', response_model=users_schema.UserResponse)
def update_user(
        user: users_schema.UserUpdate,
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)]
):

    if user.username and user.username.lower() != current_user.username:
        chk_user = db.scalar(
            select(users_model.User)
            .where(users_model.User.username == user.username.lower())
        )
        if chk_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user already exists with the same username"
            )
    
    if user.email and user.email.lower() != current_user.email:
        chk_user = db.scalar(
            select(users_model.User)
            .where(users_model.User.email == new_user.email.lower())
        )
        if chk_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user already exists with the same email"
            )
    
    update_fields = user.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)

    return current_user