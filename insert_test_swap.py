#!/usr/bin/env python3
"""
Script to insert a test vehicle swap directly into the database
"""
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    exit(1)

# Test data
ra = "06761"
swap_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
old_plate = "40-XM-45"
old_kms = 60578
old_fuel = 100
new_plate = "BA-28-FP"
new_kms = 13978
new_fuel = 50
employee_name = "Filipe Pacheco"
employee_email = "comercial@auto-prudente.com"

print(f"🔗 Connecting to database...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print(f"\n📝 Inserting test swap:")
    print(f"  RA: '{ra}'")
    print(f"  Old: {old_plate} ({old_kms} km, {old_fuel}%)")
    print(f"  New: {new_plate} ({new_kms} km, {new_fuel}%)")
    print(f"  Employee: {employee_name}")
    print(f"  Datetime: {swap_datetime}")
    
    cur.execute("""
        INSERT INTO vehicle_swaps 
        (rental_agreement_number, swap_datetime, old_plate, old_kms, old_fuel, 
         new_plate, new_kms, new_fuel, employee_name, employee_email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (ra, swap_datetime, old_plate, old_kms, old_fuel, 
          new_plate, new_kms, new_fuel, employee_name, employee_email))
    
    swap_id = cur.fetchone()[0]
    print(f"\n✅ Swap inserted with ID: {swap_id}")
    
    print(f"\n💾 Committing transaction...")
    conn.commit()
    print(f"✅ Transaction committed successfully")
    
    # Verify insertion
    cur.execute("""
        SELECT id, rental_agreement_number, old_plate, new_plate, employee_name
        FROM vehicle_swaps
        WHERE id = %s
    """, (swap_id,))
    
    result = cur.fetchone()
    if result:
        print(f"\n🔍 Verification - Record found:")
        print(f"  ID: {result[0]}")
        print(f"  RA: '{result[1]}'")
        print(f"  Old plate: {result[2]}")
        print(f"  New plate: {result[3]}")
        print(f"  Employee: {result[4]}")
    else:
        print(f"\n⚠️ Warning: Record not found after commit!")
    
    cur.close()
    conn.close()
    print("\n✅ Done! Now refresh the inspection history page.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
