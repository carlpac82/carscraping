#!/usr/bin/env python3
"""
Check existing bookings in production database to verify commission calculation
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def check_production_bookings():
    # Get DATABASE_URL from environment or use Railway
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')
    
    print("Connecting to production database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check recent bookings for AUTO PRUDENTE (ID: 157)
    print("\nChecking recent bookings for AUTO PRUDENTE (ID: 157)...")
    
    cursor.execute("""
        SELECT id, pickup_date, base_price, commission_amount, commission_rate, created_at
        FROM commission_bookings 
        WHERE commissioner_id = 157
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    bookings = cursor.fetchall()
    
    if not bookings:
        print("No bookings found for AUTO PRUDENTE")
    else:
        print(f"Found {len(bookings)} bookings:")
        for booking in bookings:
            pickup_date = booking['pickup_date']
            base_price = float(booking['base_price'] or 0)
            commission_amount = float(booking['commission_amount'] or 0)
            commission_rate = float(booking['commission_rate'] or 0)
            
            print(f"\nBooking ID: {booking['id']}")
            print(f"  Date: {pickup_date}")
            print(f"  Base Price: {base_price}")
            print(f"  Commission Rate: {commission_rate}%")
            print(f"  Commission Amount: {commission_amount}")
            
            # Check if calculation is correct
            if pickup_date and pickup_date > datetime(2026, 4, 1).date():
                expected = base_price * (commission_rate / 100.0)
                print(f"  Expected (20% no VAT): {expected:.2f}")
                rule = "After April 1 (no VAT)"
            else:
                expected = (base_price / 1.23) * 0.15
                print(f"  Expected (15% with VAT): {expected:.2f}")
                rule = "Before April 1 (with VAT)"
            
            if abs(commission_amount - expected) > 0.01:
                print(f"  *** INCORRECT CALCULATION ***")
                print(f"  Difference: {commission_amount - expected:.2f}")
            else:
                print(f"  *** CORRECT CALCULATION ***")
    
    # Check if there are any bookings with commission_amount equal to base_price
    print("\n\nChecking for bookings where commission_amount equals base_price (potential bug)...")
    cursor.execute("""
        SELECT id, commissioner_id, pickup_date, base_price, commission_amount, created_at
        FROM commission_bookings 
        WHERE ABS(commission_amount - base_price) < 0.01
        AND base_price > 0
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    problematic = cursor.fetchall()
    if problematic:
        print(f"Found {len(problematic)} bookings with commission_amount = base_price:")
        for booking in problematic:
            print(f"  ID: {booking['id']}, Date: {booking['pickup_date']}, Base: {booking['base_price']}, Commission: {booking['commission_amount']}")
    else:
        print("No bookings found with commission_amount = base_price")
    
    conn.close()

if __name__ == "__main__":
    check_production_bookings()
