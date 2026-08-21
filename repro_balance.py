from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app import models
import pytest
import os

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./repro_test.db"

def setup_module():
    Base.metadata.create_all(bind=engine)

def teardown_module():
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./repro_test.db"):
        os.remove("./repro_test.db")

def test_balance_flow():
    client = TestClient(app)
    
    # 1. Register and Login
    client.post("/api/users/register", json={
        "username": "repro_user",
        "email": "repro@example.com",
        "full_name": "Repro User",
        "password": "password"
    })
    login_res = client.post("/api/users/login", data={"username": "repro_user", "password": "password"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create Account with Initial Balance
    acc_res = client.post("/api/accounts/", json={
        "name": "Savings",
        "type": "Savings",
        "balance": 1000.0
    }, headers=headers)
    acc_id = acc_res.json()["id"]
    print(f"\nInitial Balance: {acc_res.json()['balance']}")
    assert acc_res.json()["balance"] == 1000.0
    
    # 3. Create Category
    cat_res = client.post("/api/categories/", json={
        "name": "Salary",
        "type": "income"
    }, headers=headers)
    cat_id = cat_res.json()["id"]
    
    # 4. Add Income
    client.post("/api/transactions/", json={
        "amount": 500.0,
        "type": "income",
        "description": "Salary",
        "account_id": acc_id,
        "category_id": cat_id
    }, headers=headers)
    
    acc_res = client.get("/api/accounts/", headers=headers)
    balance = acc_res.json()[0]["balance"]
    print(f"Balance after 500 income: {balance}")
    assert balance == 1500.0
    
    # 5. Add Expense
    cat_exp_res = client.post("/api/categories/", json={
        "name": "Food",
        "type": "expense"
    }, headers=headers)
    cat_exp_id = cat_exp_res.json()["id"]
    
    client.post("/api/transactions/", json={
        "amount": 200.0,
        "type": "expense",
        "description": "Lunch",
        "account_id": acc_id,
        "category_id": cat_exp_id
    }, headers=headers)
    
    acc_res = client.get("/api/accounts/", headers=headers)
    balance = acc_res.json()[0]["balance"]
    print(f"Balance after 200 expense: {balance}")
    assert balance == 1300.0
    
    # 6. Test Transfer
    acc2_res = client.post("/api/accounts/", json={
        "name": "Cash",
        "type": "Cash",
        "balance": 0.0
    }, headers=headers)
    acc2_id = acc2_res.json()["id"]
    
    client.post("/api/transactions/", json={
        "amount": 100.0,
        "type": "transfer",
        "description": "ATM Withdrawal",
        "account_id": acc_id,
        "transfer_to_account_id": acc2_id,
        "category_id": cat_id # Transfers usually don't need categories but model requires it
    }, headers=headers)
    
    # Check Savings balance
    acc_res = client.get("/api/accounts/", headers=headers)
    savings_acc = next(a for a in acc_res.json() if a["id"] == acc_id)
    cash_acc = next(a for a in acc_res.json() if a["id"] == acc2_id)
    
    print(f"Savings Balance after 100 transfer: {savings_acc['balance']}")
    print(f"Cash Balance after 100 transfer: {cash_acc['balance']}")
    
    assert savings_acc["balance"] == 1200.0
    assert cash_acc["balance"] == 100.0
    
    # 7. Check Summary Stats - Are transfers included in income/expense?
    # Usually they shouldn't be, but they affect balance.
    print(f"Savings Total Income: {savings_acc['total_income']}")
    print(f"Savings Total Expense: {savings_acc['total_expense']}")
    
    # If the user says "the current balance should be depended on income", 
    # maybe they are confused because (1000 + 500 - 200) = 1300, but they see 1200 (due to transfer).
    # OR maybe they see total_income=500, total_expense=200, and expect balance=300 (ignoring initial balance).
    
    # Let's see what the user meant.
    
if __name__ == "__main__":
    setup_module()
    try:
        test_balance_flow()
        print("Test Passed!")
    finally:
        teardown_module()
