import requests
import time

BASE_URL = "http://localhost:8002"

def test_home_page():
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Web Home Page: OK")
        else:
            print(f"❌ Web Home Page: Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ Web Home Page: Failed ({e})")

def test_submission():
    data = {
        "request_type": "Sotib olish",
        "region": "Chilonzor",
        "rooms": "2",
        "price": "400-600",
        "phone": "+998901234567"
    }
    try:
        # Simulate form posting
        response = requests.post(f"{BASE_URL}/api/request", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ Request Submission: OK (Data sent to DB & Bot)")
                print(f"   Request ID: {result.get('id')}")
            else:
                print(f"❌ Request Submission: API Error ({result})")
        else:
            print(f"❌ Request Submission: HTTP Error ({response.status_code})")
            print(response.text)
    except Exception as e:
        print(f"❌ Request Submission: Failed ({e})")

if __name__ == "__main__":
    print("--- Starting System Check ---")
    test_home_page()
    test_submission()
    print("--- Check Complete ---")
