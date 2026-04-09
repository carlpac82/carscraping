#!/usr/bin/env python3
"""
Fix the commission_bookings table schema in PostgreSQL (Railway production)
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def fix_production_schema():
    # Get DATABASE_URL from environment or use Railway
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')
    
    print("Connecting to production database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("Current commission_bookings schema:")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'commission_bookings' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]} {col[1]}")
    
    print("\nAdding missing columns...")
    
    # List of columns to add with their types
    columns_to_add = [
        ("voucher_number", "TEXT"),
        ("client_name", "TEXT"),
        ("client_email", "TEXT"),
        ("client_phone", "TEXT"),
        ("pickup_time", "TEXT"),
        ("dropoff_time", "TEXT"),
        ("pickup_location", "TEXT"),
        ("dropoff_location", "TEXT"),
        ("vehicle_group", "TEXT"),
        ("extras", "TEXT"),
        ("price", "REAL"),
        ("base_price", "REAL"),
        ("deposit", "REAL"),
        ("status", "TEXT"),
        ("commission_rate", "REAL")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE commission_bookings ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
            print(f"  Added: {col_name}")
        except Exception as e:
            print(f"  Error adding {col_name}: {e}")
    
    conn.commit()
    
    print("\nUpdated commission_bookings schema:")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'commission_bookings' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]} {col[1]}")
    
    conn.close()
    print("\nProduction schema update completed!")

if __name__ == "__main__":
    fix_production_schema()
