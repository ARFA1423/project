from app.database import SessionLocal
from app import models
from sqlalchemy import func

db = SessionLocal()
users = db.query(models.User).all()

for user in users:
    print(f"User: {user.username}")
    income = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.user_id == user.id,
        models.Transaction.type == "income"
    ).scalar() or 0
    
    expense = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.user_id == user.id,
        models.Transaction.type == "expense"
    ).scalar() or 0
    
    print(f"  Total Income: {income}")
    print(f"  Total Expense: {expense}")
    print(f"  Net Income: {income - expense}")
    
    accounts = db.query(models.Account).filter(models.Account.user_id == user.id).all()
    total_assets = 0
    for acc in accounts:
        acc_income = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.account_id == acc.id,
            models.Transaction.type == "income"
        ).scalar() or 0
        acc_expense = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.account_id == acc.id,
            models.Transaction.type == "expense"
        ).scalar() or 0
        
        transfer_in = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.transfer_to_account_id == acc.id,
            models.Transaction.type == "transfer"
        ).scalar() or 0
        transfer_out = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.account_id == acc.id,
            models.Transaction.type == "transfer"
        ).scalar() or 0
        
        acc_balance = acc.initial_balance + acc_income - acc_expense + transfer_in - transfer_out
        total_assets += acc_balance
        print(f"  Account: {acc.name}, Initial: {acc.initial_balance}, Income: {acc_income}, Expense: {acc_expense}, T_In: {transfer_in}, T_Out: {transfer_out}, Balance: {acc_balance}")
    
    print(f"  Total Assets: {total_assets}")

db.close()
