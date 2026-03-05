#!/usr/bin/env python3
"""
Check vans pricing in database
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
    # Check if vans_pricing table exists and has data
    print("\n📋 Checking vans_pricing table:")
    cur.execute("""
        SELECT * FROM vans_pricing ORDER BY id DESC LIMIT 1
    """)
    row = cur.fetchone()
    
    if row:
        print(f"✅ Found vans pricing:")
        print(f"  ID: {row[0]}")
        print(f"  C3: 1day={row[1]}, 2days={row[2]}, 3days={row[3]}")
        print(f"  C4: 1day={row[4]}, 2days={row[5]}, 3days={row[6]}")
        print(f"  C5: 1day={row[7]}, 2days={row[8]}, 3days={row[9]}")
    else:
        print("❌ No vans pricing found in database")
        print("💡 Need to save prices in Automated Prices → Carrinhas Comerciais first")
    
finally:
    cur.close()
    conn.close()
