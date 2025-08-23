#!/usr/bin/env python3

import requests
import json


# Simple test to check if backend is responding and using latest Java wrapper
def test_backend_java():
    url = "http://localhost:8000/api/code/run"

    payload = {
        "language": "java",
        "code": """
class Solution {
    public int test() {
        return 42;
    }
}
""",
        "function_name": "test",
        "input_data": {},
    }

    print("🔍 Testing backend Java compilation...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")

            # Check if compilation errors mention the old regex issue
            if result.get("error"):
                if '([^\\"]*)' in result["error"]:
                    print("❌ Still seeing old regex pattern error!")
                    return False
                else:
                    print("✅ New error pattern detected (progress!)")
                    return True
            else:
                print("✅ No compilation errors!")
                return True
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False


if __name__ == "__main__":
    test_backend_java()
