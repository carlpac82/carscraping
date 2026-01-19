#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/filipepacheco/CascadeProjects/carscraping')

from database import _db_connect
import json

conn = _db_connect()
cursor = conn.cursor()

# Try PostgreSQL first
try:
    cursor.execute("SELECT rental_agreement_number, license_plate, extracted_data FROM rental_agreements WHERE rental_agreement_number LIKE %s", ('06716%',))
except:
    # Fallback to SQLite
    cursor.execute("SELECT rental_agreement_number, license_plate, extracted_data FROM rental_agreements WHERE rental_agreement_number LIKE ?", ('06716%',))

row = cursor.fetchone()
if row:
    print(f"✅ RA Found: {row[0]}")
    print(f"📋 License Plate: {row[1]}")
    
    if row[2]:
        try:
            data = json.loads(row[2])
            print(f"\n📋 Extracted Data Keys ({len(data)} fields):")
            print(f"   {list(data.keys())}")
            print(f"\n📋 Full Extracted Data:")
            for key, value in data.items():
                print(f"   {key}: {value}")
        except Exception as e:
            print(f"❌ Error parsing extracted_data: {e}")
            print(f"Raw data (first 500 chars): {row[2][:500]}")
    else:
        print("⚠️  No extracted_data found")
else:
    print("❌ RA not found")

conn.close()
