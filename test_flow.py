from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("REGISTERING...")
res = client.post("/register", data={
    "full_name": "Test User",
    "username": "testuser",
    "email": "test@test.com",
    "password": "password123",
    "confirm_password": "password123"
}, follow_redirects=False)
print("REGISTER:", res.status_code, res.headers.get("location"))

print("DASHBOARD:")
res2 = client.get("/dashboard", follow_redirects=False)
print("DASHBOARD (with Session):", res2.status_code)

print("LOGIN SUCCESS:")
res3 = client.post("/login", data={
    "username": "testuser",
    "password": "password123"
}, follow_redirects=False)
print("LOGIN:", res3.status_code, res3.headers.get("location"))

print("LOGIN FAIL:")
res4 = client.post("/login", data={
    "username": "testuser",
    "password": "wrong"
}, follow_redirects=False)
print("LOGIN FAIL:", res4.status_code)
