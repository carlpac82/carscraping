#!/usr/bin/env python3
"""
Debug script to check vehicle_swaps table in PostgreSQL
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    exit(1)

print(f"🔗 Connecting to database...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check if vehicle_swaps table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'vehicle_swaps'
        )
    """)
    table_exists = cur.fetchone()[0]
    print(f"📋 Table vehicle_swaps exists: {table_exists}")
    
    if table_exists:
        # Count total swaps
        cur.execute("SELECT COUNT(*) FROM vehicle_swaps")
        total = cur.fetchone()[0]
        print(f"📊 Total swaps in database: {total}")
        
        # Check for RA 06761
        cur.execute("""
            SELECT id, rental_agreement_number, swap_datetime, old_plate, new_plate, 
                   employee_name, created_at
            FROM vehicle_swaps
            WHERE rental_agreement_number = %s OR rental_agreement_number LIKE %s
            ORDER BY swap_datetime DESC
        """, ('06761', '06761%'))
        
        swaps = cur.fetchall()
        print(f"\n🔍 Swaps for RA 06761: {len(swaps)}")
        
        if swaps:
            for swap in swaps:
                print(f"\n  ID: {swap[0]}")
                print(f"  RA: '{swap[1]}' (length: {len(swap[1])})")
                print(f"  Datetime: {swap[2]}")
                print(f"  Old plate: {swap[3]}")
                print(f"  New plate: {swap[4]}")
                print(f"  Employee: {swap[5]}")
                print(f"  Created: {swap[6]}")
        else:
            print("  ⚠️ No swaps found for RA 06761")
            
            # Check all RAs in vehicle_swaps
            cur.execute("""
                SELECT DISTINCT rental_agreement_number 
                FROM vehicle_swaps 
                ORDER BY rental_agreement_number DESC 
                LIMIT 10
            """)
            all_ras = cur.fetchall()
            print(f"\n📋 Last 10 RAs in vehicle_swaps:")
            for ra in all_ras:
                print(f"  - '{ra[0]}' (length: {len(ra[0])})")
    
    cur.close()
    conn.close()
    print("\n✅ Connection closed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
