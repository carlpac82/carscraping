#!/usr/bin/env python3
"""
Script to check commissioners tables structure and data
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')

def check_tables():
    """Check commissioners and commission_bookings tables"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=" * 80)
    print("CHECKING COMMISSIONERS TABLES")
    print("=" * 80)
    
    # Check commissioners table structure
    print("\n📋 COMMISSIONERS TABLE STRUCTURE:")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'commissioners'
        ORDER BY ordinal_position
    """)
    
    commissioners_cols = cursor.fetchall()
    if commissioners_cols:
        for col in commissioners_cols:
            print(f"  ✓ {col['column_name']:30} {col['data_type']:20} NULL: {col['is_nullable']}")
    else:
        print("  ❌ Table 'commissioners' does not exist!")
    
    # Check commission_bookings table structure
    print("\n📋 COMMISSION_BOOKINGS TABLE STRUCTURE:")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'commission_bookings'
        ORDER BY ordinal_position
    """)
    
    bookings_cols = cursor.fetchall()
    if bookings_cols:
        for col in bookings_cols:
            print(f"  ✓ {col['column_name']:30} {col['data_type']:20} NULL: {col['is_nullable']}")
    else:
        print("  ❌ Table 'commission_bookings' does not exist!")
    
    # Check required columns
    print("\n🔍 CHECKING REQUIRED COLUMNS:")
    
    required_commissioners_cols = ['id', 'name', 'email', 'username', 'password_hash', 
                                   'commission_rate', 'enabled', 'voucher_prefix', 'phone']
    commissioners_col_names = [col['column_name'] for col in commissioners_cols]
    
    for col in required_commissioners_cols:
        if col in commissioners_col_names:
            print(f"  ✓ commissioners.{col}")
        else:
            print(f"  ❌ commissioners.{col} - MISSING!")
    
    required_bookings_cols = ['id', 'commissioner_id', 'voucher_number', 'client_name', 
                             'client_email', 'vehicle_group', 'insurance_type', 'base_price',
                             'premium_insurance', 'road_tax', 'extras_total', 'rental_days',
                             'total_amount', 'value_adjustment', 'price', 'deposit', 'status']
    bookings_col_names = [col['column_name'] for col in bookings_cols]
    
    for col in required_bookings_cols:
        if col in bookings_col_names:
            print(f"  ✓ commission_bookings.{col}")
        else:
            print(f"  ❌ commission_bookings.{col} - MISSING!")
    
    # Count records
    print("\n📊 RECORD COUNTS:")
    cursor.execute("SELECT COUNT(*) as count FROM commissioners")
    comm_count = cursor.fetchone()['count']
    print(f"  Commissioners: {comm_count}")
    
    cursor.execute("SELECT COUNT(*) as count FROM commission_bookings")
    booking_count = cursor.fetchone()['count']
    print(f"  Bookings: {booking_count}")
    
    # Show sample commissioners
    if comm_count > 0:
        print("\n👥 SAMPLE COMMISSIONERS:")
        cursor.execute("""
            SELECT id, name, username, voucher_prefix, email, enabled
            FROM commissioners
            LIMIT 5
        """)
        for comm in cursor.fetchall():
            print(f"  ID: {comm['id']:3} | {comm['name']:30} | User: {comm['username'] or 'NULL':10} | Serie: {comm['voucher_prefix'] or 'NULL':10} | Active: {comm['enabled']}")
    
    conn.close()
    print("\n" + "=" * 80)
    print("CHECK COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    check_tables()
