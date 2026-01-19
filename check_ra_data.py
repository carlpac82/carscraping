#!/usr/bin/env python3
import os
import sys
import json
import sqlite3

# Use SQLite local
conn = sqlite3.connect('fleet_management.db')
cursor = conn.cursor()

# Get the most recent RA
cursor.execute("SELECT rental_agreement_number, license_plate, extracted_data FROM rental_agreements ORDER BY created_at DESC LIMIT 5")
rows = cursor.fetchall()

print(f"📋 Found {len(rows)} recent RAs:\n")
for row in rows:
    print(f"   • RA: {row[0]} | Plate: {row[1]}")

print("\n" + "="*80)
print("Checking most recent RA...")
print("="*80 + "\n")

cursor.execute("SELECT rental_agreement_number, license_plate, extracted_data FROM rental_agreements ORDER BY created_at DESC LIMIT 1")

row = cursor.fetchone()
if row:
    print(f"✅ RA Found: {row[0]}")
    print(f"📋 License Plate: {row[1]}")
    
    if row[2]:
        try:
            data = json.loads(row[2])
            print(f"\n📋 Extracted Data Keys: {list(data.keys())}")
            print(f"\n📋 Full Extracted Data:")
            for key, value in data.items():
                print(f"   {key}: {value}")
            
            print(f"\n🔍 Checking specific fields:")
            print(f"   clientName: {data.get('clientName', 'NOT FOUND')}")
            print(f"   pickupLocation: {data.get('pickupLocation', 'NOT FOUND')}")
            print(f"   email: {data.get('email', 'NOT FOUND')}")
        except Exception as e:
            print(f"❌ Error parsing extracted_data: {e}")
            print(f"Raw data: {row[2]}")
    else:
        print("⚠️  No extracted_data found")
else:
    print("❌ RA not found")

conn.close()
