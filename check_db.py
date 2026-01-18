import psycopg2
import os

# Connect to Railway PostgreSQL
DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ Connected to database")
    
    # Check inspections
    cursor.execute("""
        SELECT inspection_number, vehicle_plate, contract_number, 
               inspection_type, inspector_name, created_at
        FROM vehicle_inspections
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    print(f"\n📊 Found {len(rows)} inspections:\n")
    
    for row in rows:
        print(f"  {row[3]:8} | {row[1]:12} | RA: {row[2]:10} | {row[4]:20} | {row[5]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
