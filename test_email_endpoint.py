#!/usr/bin/env python3
"""
Test script to verify email sending endpoint
"""
import requests
import json

# Railway URL
BASE_URL = "https://carscraping.up.railway.app"

# Test data
test_data = {
    "type": "checkout",
    "photos": {},
    "damages": [],
    "observations": "Test observation",
    "fuelLevel": 100,
    "odometerReading": 12345,
    "plate": "TEST-123",
    "ra": "TEST-RA",
    "receptionist": "Test User",
    "date": "2026-01-19",
    "time": "19:00",
    "client_email": "test@example.com",
    "send_email": True,
    "vehicle_id": None,
    "damageCroqui": ""
}

print("🧪 Testing /api/save-inspection endpoint...")
print(f"📧 Email: {test_data['client_email']}")
print(f"✅ send_email: {test_data['send_email']}")
print()

try:
    response = requests.post(
        f"{BASE_URL}/api/save-inspection",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
