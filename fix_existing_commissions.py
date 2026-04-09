#!/usr/bin/env python3
"""
Fix existing commission bookings with incorrect calculation
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def fix_existing_commissions():
    # Get DATABASE_URL from environment or use Railway
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')
    
    print("Connecting to production database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Find bookings with incorrect commission calculation
    # Specifically looking for bookings after April 1, 2026 with wrong commission
    print("\nFinding bookings with incorrect commission calculation...")
    
    cursor.execute("""
        SELECT id, commissioner_id, pickup_date, base_price, commission_amount, commission_rate
        FROM commission_bookings 
        WHERE pickup_date > '2026-04-01'
        AND base_price > 0
        AND ABS(commission_amount - (base_price * COALESCE(commission_rate, 20.0) / 100.0)) > 0.01
        ORDER BY pickup_date DESC
    """)
    
    problematic_bookings = cursor.fetchall()
    
    if not problematic_bookings:
        print("No bookings found with incorrect commission calculation")
        return
    
    print(f"Found {len(problematic_bookings)} bookings with incorrect commission:")
    
    # Fix each booking
    fixed_count = 0
    for booking in problematic_bookings:
        booking_id = booking['id']
        pickup_date = booking['pickup_date']
        base_price = float(booking['base_price'] or 0)
        current_commission = float(booking['commission_amount'] or 0)
        commission_rate = float(booking['commission_rate'] or 20.0)
        
        # Calculate correct commission
        if pickup_date > datetime(2026, 4, 1).date():
            correct_commission = base_price * (commission_rate / 100.0)
            rule = "After April 1 (no VAT)"
        else:
            correct_commission = (base_price / 1.23) * 0.15
            rule = "Before April 1 (with VAT)"
        
        print(f"\nBooking ID: {booking_id}")
        print(f"  Date: {pickup_date}")
        print(f"  Base Price: {base_price}")
        print(f"  Current Commission: {current_commission}")
        print(f"  Correct Commission: {correct_commission:.2f}")
        print(f"  Rule: {rule}")
        
        # Update the booking
        cursor.execute("""
            UPDATE commission_bookings 
            SET commission_amount = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (correct_commission, booking_id))
        
        fixed_count += 1
        print(f"  -> Fixed!")
    
    conn.commit()
    print(f"\nSuccessfully fixed {fixed_count} bookings!")
    
    # Verify the fixes
    print("\nVerifying fixes...")
    cursor.execute("""
        SELECT id, pickup_date, base_price, commission_amount, commission_rate
        FROM commission_bookings 
        WHERE pickup_date > '2026-04-01'
        AND base_price > 0
        ORDER BY pickup_date DESC
        LIMIT 5
    """)
    
    recent_bookings = cursor.fetchall()
    print("\nRecent bookings after fix:")
    for booking in recent_bookings:
        pickup_date = booking['pickup_date']
        base_price = float(booking['base_price'] or 0)
        commission_amount = float(booking['commission_amount'] or 0)
        commission_rate = float(booking['commission_rate'] or 0)
        
        expected = base_price * (commission_rate / 100.0)
        print(f"  ID: {booking['id']}, Date: {pickup_date}, Base: {base_price}, Commission: {commission_amount}, Expected: {expected:.2f}")
        
        if abs(commission_amount - expected) > 0.01:
            print(f"    *** STILL INCORRECT ***")
        else:
            print(f"    *** CORRECT ***")
    
    conn.close()

if __name__ == "__main__":
    fix_existing_commissions()
