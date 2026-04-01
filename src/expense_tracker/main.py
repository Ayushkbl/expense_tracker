from fastapi import FastAPI

from expense_tracker.users.routers import router as users_router
from expense_tracker.expense.routers import router as expense_router

app = FastAPI()

app.include_router(users_router, prefix="/api/users", tags=["Users",])
app.include_router(expense_router, prefix="/api/expenses", tags=["Expense",])