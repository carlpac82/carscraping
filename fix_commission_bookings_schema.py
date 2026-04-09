#!/usr/bin/env python3
"""
Fix the commission_bookings table schema to match what the code expects
"""
import sqlite3
import sys

def fix_schema():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    print("Current commission_bookings schema:")
    cursor.execute("PRAGMA table_info(commission_bookings)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} {col[2]}")
    
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
            cursor.execute(f"ALTER TABLE commission_bookings ADD COLUMN {col_name} {col_type}")
            print(f"  Added: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"  Already exists: {col_name}")
            else:
                print(f"  Error adding {col_name}: {e}")
    
    conn.commit()
    
    print("\nUpdated commission_bookings schema:")
    cursor.execute("PRAGMA table_info(commission_bookings)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} {col[2]}")
    
    conn.close()
    print("\nSchema update completed!")

if __name__ == "__main__":
    fix_schema()
