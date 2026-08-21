import sys
import os
sys.path.insert(0, r"c:\Users\User\OneDrive\Documents\project\expentia")
from fastapi.testclient import TestClient
from app.main import app
import traceback

client = TestClient(app)
try:
    response = client.get("/")
    print("STATUS", response.status_code)
    print("BODY", response.text)
except Exception as e:
    traceback.print_exc()
