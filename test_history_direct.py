#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the function directly
from main import _db_connect
import logging

logging.basicConfig(level=logging.INFO)

try:
    print("🔍 Testing history API logic directly...")
    conn = _db_connect()
    
    # Detect database type
    is_postgres = False
    conn_type = type(conn).__name__
    
    if 'psycopg' in conn_type.lower() or conn_type == 'connection':
        is_postgres = True
    elif os.getenv('DATABASE_URL'):
        is_postgres = True
    
    print(f"Database type: {'PostgreSQL' if is_postgres else 'SQLite'}")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT inspection_number, vehicle_plate, contract_number, 
               inspection_type, inspector_name, created_at, 
               fuel_level, odometer_reading, damage_count, status
        FROM vehicle_inspections
        ORDER BY created_at DESC
        LIMIT 200
    """)
    rows = cursor.fetchall()
    
    print(f"\n📊 Found {len(rows)} inspections")
    
    # Group by plate + RA
    grouped = {}
    for row in rows:
        plate = row[1]
        ra = row[2]
        inspection_type = row[3]
        key = f"{plate}_{ra}"
        
        print(f"  - {inspection_type:8} | {plate:12} | RA: {ra:10} | {row[5]}")
        
        inspection_data = {
            "inspection_number": row[0],
            "vehicle_plate": row[1],
            "contract_number": row[2],
            "inspection_type": row[3],
            "inspector_name": row[4],
            "created_at": str(row[5]) if row[5] else None,
            "fuel_level": row[6],
            "odometer_reading": row[7],
            "damage_count": row[8],
            "status": row[9]
        }
        
        if key not in grouped:
            grouped[key] = {
                "vehicle_plate": plate,
                "contract_number": ra,
                "checkout": None,
                "checkin": None,
                "latest_date": row[5]
            }
        
        if row[3] == 'checkout':
            if not grouped[key]["checkout"]:
                grouped[key]["checkout"] = inspection_data
        elif row[3] == 'checkin':
            if not grouped[key]["checkin"]:
                grouped[key]["checkin"] = inspection_data
    
    # Convert to list
    contracts = list(grouped.values())
    contracts.sort(key=lambda x: x["latest_date"] if x["latest_date"] else "", reverse=True)
    
    print(f"\n✅ Grouped into {len(contracts)} contracts:")
    for contract in contracts:
        print(f"\n  Plate: {contract['vehicle_plate']}")
        print(f"  RA: {contract['contract_number']}")
        print(f"  Checkout: {'✅' if contract['checkout'] else '❌'}")
        print(f"  Checkin: {'✅' if contract['checkin'] else '❌'}")
        print(f"  Latest: {contract['latest_date']}")
    
    conn.close()
    
    print("\n✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
