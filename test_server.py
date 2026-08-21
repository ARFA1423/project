import threading
import time
import urllib.request
import urllib.error
import uvicorn
import traceback
from app.main import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")

t = threading.Thread(target=run_server, daemon=True)
t.start()
time.sleep(3) # Wait for server to start

try:
    print("Making request...")
    req = urllib.request.Request("http://127.0.0.1:8001/")
    with urllib.request.urlopen(req) as response:
        print("STATUS:", response.status)
        print("BODY:", response.read().decode()[:100])
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code)
    try:
        print("BODY:", e.read().decode())
    except Exception as ex:
        print("Could not read body:", ex)
except Exception as e:
    traceback.print_exc()

print("DONE")
