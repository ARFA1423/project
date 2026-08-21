import urllib.request
import urllib.error
import sys

try:
    req = urllib.request.Request("http://127.0.0.1:8000/")
    with urllib.request.urlopen(req) as response:
        print("STATUS:", response.status)
        print("BODY:", response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code)
    try:
        print("BODY:", e.read().decode())
    except:
        pass
except Exception as e:
    print("ERROR:", e)
