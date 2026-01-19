#!/usr/bin/env python3
import os
import sys
import json

# Determine which DB to use
_USE_NEW_DB = os.getenv('USE_POSTGRES', 'true').lower() == 'true'

if _USE_NEW_DB:
    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'fleet_management'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    cursor = conn.cursor()
    cursor.execute("SELECT rental_agreement_number, license_plate, extracted_data FROM rental_agreements WHERE rental_agreement_number LIKE %s", ('06716%',))
else:
    import sqlite3
    conn = sqlite3.connect('fleet_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT rental_agreement_number, license_plate, extracted_data FROM rental_agreements WHERE rental_agreement_number LIKE ?", ('06716%',))

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
