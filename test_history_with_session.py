import requests
import json

# Create session and login first
session = requests.Session()

# Try to access history (should work if we're logged in via browser)
try:
    response = session.get('http://127.0.0.1:5000/api/inspections/history', 
                          cookies={'session': 'test'})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ API Response:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()
