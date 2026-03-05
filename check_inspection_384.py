#!/usr/bin/env python3
"""
Check inspection 384 details
"""
import os
import psycopg2

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    exit(1)

print(f"🔗 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    # Get inspection 384 details
    print("\n📋 Inspection 384 details:")
    cur.execute("""
        SELECT id, contract_number, vehicle_plate, inspection_type, 
               odometer_reading, fuel_level, inspector_name, 
               created_at, status
        FROM vehicle_inspections
        WHERE id = 384
    """)
    row = cur.fetchone()
    
    if row:
        print(f"  ID: {row[0]}")
        print(f"  Contract: {row[1]}")
        print(f"  Plate: {row[2]}")
        print(f"  Type: {row[3]}")
        print(f"  Odometer: {row[4]}")
        print(f"  Fuel: {row[5]}")
        print(f"  Inspector: {row[6]}")
        print(f"  Created: {row[7]}")
        print(f"  Status: {row[8]}")
    else:
        print("  ❌ Not found")
    
    # Check what the frontend is looking for
    print("\n🔍 What frontend is looking for:")
    print("  Plate: AT-28-NX")
    print("  RA: 06932-09")
    print("  Type: checkin")
    
    # Search for matching inspections
    print("\n📋 Searching for inspections matching frontend query:")
    cur.execute("""
        SELECT id, contract_number, vehicle_plate, inspection_type, status
        FROM vehicle_inspections
        WHERE vehicle_plate = 'AT-28-NX'
          AND contract_number LIKE '06932%'
          AND inspection_type = 'checkin'
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    
    if rows:
        print(f"  ✅ Found {len(rows)} matching inspection(s):")
        for row in rows:
            print(f"    - ID {row[0]}: {row[1]} | {row[2]} | {row[3]} | status={row[4]}")
    else:
        print("  ❌ No matching inspections found")
        
    # Check all inspections for this RA
    print("\n📋 All inspections for RA 06932:")
    cur.execute("""
        SELECT id, contract_number, vehicle_plate, inspection_type, status, created_at
        FROM vehicle_inspections
        WHERE contract_number LIKE '06932%'
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    
    print(f"  Found {len(rows)} total inspection(s):")
    for row in rows:
        print(f"    - ID {row[0]}: {row[1]} | {row[2]} | {row[3]} | status={row[4]} | {row[5]}")
    
finally:
    cur.close()
    conn.close()
