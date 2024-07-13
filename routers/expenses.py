from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from decimal import Decimal
from database import expenses_db, groups_db
from auth import get_current_user
from utils import round_currency, calculate_split_amounts, validate_split_details, simplify_debts
import uuid

router = APIRouter(prefix="/expenses", tags=["expenses"])

class ExpenseCreate(BaseModel):
    group_id: str
    description: str
    amount: Decimal
    paid_by: str
    split_type: str  # "equal", "percentage", or "fixed"
    split_details: Dict[str, Decimal]  # For percentage and fixed splits

class ExpenseUpdate(BaseModel):
    description: str
    amount: Decimal
    paid_by: str
    split_type: str
    split_details: Dict[str, Decimal]

class Expense(BaseModel):
    id: str
    group_id: str
    description: str
    amount: Decimal
    paid_by: str
    split_type: str
    split_details: Dict[str, Decimal]

@router.post("/", response_model=Expense)
async def create_expense(expense: ExpenseCreate, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(expense.group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Validate and calculate split details
    if not validate_split_details(expense.amount, expense.split_type, expense.split_details):
        raise HTTPException(status_code=400, detail="Invalid split details")
    
    split_amounts = calculate_split_amounts(expense.amount, expense.split_type, expense.split_details)

    expense_id = str(uuid.uuid4())
    new_expense = {
        "id": expense_id,
        "group_id": expense.group_id,
        "description": expense.description,
        "amount": float(expense.amount),
        "paid_by": expense.paid_by,
        "split_type": expense.split_type,
        "split_details": {k: float(v) for k, v in split_amounts.items()}
    }
    expenses_db.put(new_expense, key=expense_id)
    return Expense(**new_expense)

@router.get("/{group_id}", response_model=List[Expense])
async def get_group_expenses(group_id: str, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    
    all_expenses = expenses_db.fetch().items
    group_expenses = [Expense(**expense) for expense in all_expenses if expense["group_id"] == group_id]
    return group_expenses

@router.get("/{group_id}/{expense_id}", response_model=Expense)
async def get_expense(group_id: str, expense_id: str, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    
    expense = expenses_db.get(expense_id)
    if not expense or expense["group_id"] != group_id:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return Expense(**expense)

@router.put("/{group_id}/{expense_id}", response_model=Expense)
async def update_expense(group_id: str, expense_id: str, expense_update: ExpenseUpdate, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    
    expense = expenses_db.get(expense_id)
    if not expense or expense["group_id"] != group_id:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Validate and calculate split details
    if not validate_split_details(expense_update.amount, expense_update.split_type, expense_update.split_details):
        raise HTTPException(status_code=400, detail="Invalid split details")
    
    split_amounts = calculate_split_amounts(expense_update.amount, expense_update.split_type, expense_update.split_details)

    updated_expense = {
        "id": expense_id,
        "group_id": group_id,
        "description": expense_update.description,
        "amount": float(expense_update.amount),
        "paid_by": expense_update.paid_by,
        "split_type": expense_update.split_type,
        "split_details": {k: float(v) for k, v in split_amounts.items()}
    }
    expenses_db.put(updated_expense, key=expense_id)
    return Expense(**updated_expense)

@router.delete("/{group_id}/{expense_id}")
async def delete_expense(group_id: str, expense_id: str, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    
    expense = expenses_db.get(expense_id)
    if not expense or expense["group_id"] != group_id:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    expenses_db.delete(expense_id)
    return {"message": "Expense deleted successfully"}

@router.get("/{group_id}/balances")
async def get_group_balances(group_id: str, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    
    all_expenses = expenses_db.fetch().items
    group_expenses = [expense for expense in all_expenses if expense["group_id"] == group_id]
    
    balances = {member: Decimal(0) for member in group["members"]}
    
    for expense in group_expenses:
        paid_by = expense["paid_by"]
        amount = Decimal(expense["amount"])
        split_details = expense["split_details"]
        
        balances[paid_by] += amount
        for member, share in split_details.items():
            balances[member] -= Decimal(share)
    
    return {member: round_currency(balance) for member, balance in balances.items()}

@router.get("/user/balances")
async def get_user_balances(current_user: dict = Depends(get_current_user)):
    user_groups = [group for group in groups_db.fetch().items if current_user["username"] in group["members"]]
    user_balances = {}
    
    for group in user_groups:
        group_id = group["id"]
        group_balances = await get_group_balances(group_id, current_user)
        user_balances[group["name"]] = group_balances[current_user["username"]]
    
    return user_balances

@router.post("/{group_id}/settle")
async def settle_group_debts(group_id: str, current_user: dict = Depends(get_current_user)):
    group = groups_db.get(group_id)
    if not group or current_user["username"] not in group["members"]:
        raise HTTPException(status_code=404, detail="Group not found")
    
    balances = await get_group_balances(group_id, current_user)
    
    # Implement debt simplification algorithm
    transactions = simplify_debts(balances)
    
    return [{"from": from_user, "to": to_user, "amount": round_currency(Decimal(amount))} 
            for from_user, to_user, amount in transactions]