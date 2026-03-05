#!/usr/bin/env python3
"""
Fix contract_number for inspection 384
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
    # Check current value
    print("\n📋 Current inspection 384:")
    cur.execute("SELECT id, contract_number, vehicle_plate FROM vehicle_inspections WHERE id = 384")
    row = cur.fetchone()
    print(f"  ID: {row[0]}, Contract: {row[1]}, Plate: {row[2]}")
    
    # Update contract_number
    print("\n🔧 Updating contract_number to '06932-09'...")
    cur.execute("""
        UPDATE vehicle_inspections
        SET contract_number = '06932-09'
        WHERE id = 384
    """)
    
    conn.commit()
    
    # Verify
    print("\n✅ Updated inspection 384:")
    cur.execute("SELECT id, contract_number, vehicle_plate FROM vehicle_inspections WHERE id = 384")
    row = cur.fetchone()
    print(f"  ID: {row[0]}, Contract: {row[1]}, Plate: {row[2]}")
    
    # Test the query that frontend uses
    print("\n🔍 Testing frontend query:")
    cur.execute("""
        SELECT id, contract_number, vehicle_plate, inspection_type
        FROM vehicle_inspections
        WHERE vehicle_plate = 'AT-28-NX'
          AND contract_number LIKE '06932%'
          AND inspection_type = 'checkin'
    """)
    rows = cur.fetchall()
    
    if rows:
        print(f"  ✅ Found {len(rows)} matching inspection(s):")
        for row in rows:
            print(f"    - ID {row[0]}: {row[1]} | {row[2]} | {row[3]}")
    else:
        print("  ❌ Still not found!")
    
finally:
    cur.close()
    conn.close()
