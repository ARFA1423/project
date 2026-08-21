from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
from app import models
import os

# Use a separate test database for verification
TEST_DB = "verify_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///./{TEST_DB}"

def setup_module():
    Base.metadata.create_all(bind=engine)

def teardown_module():
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_balance_verification():
    client = TestClient(app)
    
    # 1. Register & Login (using form data for login)
    client.post("/api/users/register", json={
        "username": "verify_user",
        "email": "verify@example.com",
        "full_name": "Verify User",
        "password": "password"
    })
    login_res = client.post("/api/users/login", data={"username": "verify_user", "password": "password"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create Accounts
    # Savings: 1000
    # Cash: 0
    savings_res = client.post("/api/accounts/", json={"name": "Savings", "type": "Savings", "initial_balance": 1000.0}, headers=headers)
    savings_id = savings_res.json()["id"]
    
    cash_res = client.post("/api/accounts/", json={"name": "Cash", "type": "Cash", "initial_balance": 0.0}, headers=headers)
    cash_id = cash_res.json()["id"]
    
    # Create Categories
    inc_cat = client.post("/api/categories/", json={"name": "Salary", "type": "income"}, headers=headers).json()["id"]
    exp_cat = client.post("/api/categories/", json={"name": "Food", "type": "expense"}, headers=headers).json()["id"]
    
    # 3. Add Income: 500 to Savings
    client.post("/api/transactions/", json={
        "amount": 500.0, "type": "income", "account_id": savings_id, "category_id": inc_cat
    }, headers=headers)
    
    # Balance should be 1500
    res = client.get("/api/accounts/", headers=headers).json()
    savings = next(a for a in res if a["id"] == savings_id)
    assert savings["balance"] == 1500.0
    print(f"PASS: Savings balance after income: {savings['balance']}")
    
    # 4. Add Expense: 200 from Savings
    client.post("/api/transactions/", json={
        "amount": 200.0, "type": "expense", "account_id": savings_id, "category_id": exp_cat
    }, headers=headers)
    
    # Balance should be 1300
    res = client.get("/api/accounts/", headers=headers).json()
    savings = next(a for a in res if a["id"] == savings_id)
    assert savings["balance"] == 1300.0
    print(f"PASS: Savings balance after expense: {savings['balance']}")
    
    # 5. Transfer: 100 from Savings to Cash
    client.post("/api/transactions/", json={
        "amount": 100.0, "type": "transfer", "account_id": savings_id, "transfer_to_account_id": cash_id, "category_id": inc_cat
    }, headers=headers)
    
    # Savings: 1200, Cash: 100
    res = client.get("/api/accounts/", headers=headers).json()
    savings = next(a for a in res if a["id"] == savings_id)
    cash = next(a for a in res if a["id"] == cash_id)
    assert savings["balance"] == 1200.0
    assert cash["balance"] == 100.0
    print(f"PASS: Savings ({savings['balance']}) and Cash ({cash['balance']}) after transfer")
    
    # 6. Verify Statistics Summary
    stats = client.get("/api/statistics/summary", headers=headers).json()
    assert stats["total_assets"] == 1300.0 # 1200 + 100
    assert stats["total_income"] == 500.0
    assert stats["total_expense"] == 200.0
    print(f"PASS: Total assets: {stats['total_assets']}, Income: {stats['total_income']}, Expense: {stats['total_expense']}")
    
    # 7. Delete Income Transaction
    # Find the income transaction
    txs = client.get("/api/transactions/", headers=headers).json()
    inc_tx_id = next(t for t in txs if t["type"] == "income")["id"]
    client.delete(f"/api/transactions/{inc_tx_id}", headers=headers)
    
    # Balance should revert: Savings: 1200 - 500 = 700
    res = client.get("/api/accounts/", headers=headers).json()
    savings = next(a for a in res if a["id"] == savings_id)
    assert savings["balance"] == 700.0
    print(f"PASS: Savings balance after income deletion: {savings['balance']}")
    
    # Total Assets should be 700 + 100 = 800
    stats = client.get("/api/statistics/summary", headers=headers).json()
    assert stats["total_assets"] == 800.0
    print(f"PASS: Total assets after deletion: {stats['total_assets']}")

if __name__ == "__main__":
    setup_module()
    try:
        test_balance_verification()
        print("\nALL VERIFICATION TESTS PASSED!")
    finally:
        teardown_module()
