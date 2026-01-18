import requests
import json

try:
    response = requests.get('http://127.0.0.1:5000/api/inspections/history')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"OK: {data.get('ok')}")
        print(f"Contracts: {len(data.get('contracts', []))}")
        
        if data.get('contracts'):
            for contract in data['contracts']:
                print(f"\n  Plate: {contract['vehicle_plate']}")
                print(f"  RA: {contract['contract_number']}")
                print(f"  Checkout: {contract['checkout'] is not None}")
                print(f"  Checkin: {contract['checkin'] is not None}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
