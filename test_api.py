import requests

BASE = "http://localhost:5000"

def test(method, url, payload=None, label=""):
    print(f"\n=== {label} ===")
    try:
        resp = requests.post(url, json=payload, timeout=10) if method == "POST" else requests.get(url, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test("GET", f"{BASE}/health", label="1. Health Check")
    test("POST", f"{BASE}/chat", payload={"message": "Test"}, label="2. Valid Request")
    test("POST", f"{BASE}/chat", payload={"message": "Test"}, label="3. Cache Test (Repeat)")
    test("POST", f"{BASE}/chat", payload={"message": ""}, label="4. Empty Message")
    test("POST", f"{BASE}/chat", payload={"message": "x" * 1001}, label="5. Long Message (1001 chars)")