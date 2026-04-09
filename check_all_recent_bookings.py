#!/usr/bin/env python3
"""
Check all recent bookings in production to understand the commission calculation issue
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def check_all_recent_bookings():
    # Get DATABASE_URL from environment or use Railway
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')
    
    print("Connecting to production database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check all recent bookings (last 30 days)
    print("\nChecking all bookings in the last 30 days...")
    
    cursor.execute("""
        SELECT cb.id, cb.commissioner_id, c.username, cb.pickup_date, 
               cb.base_price, cb.commission_amount, cb.commission_rate,
               cb.created_at
        FROM commission_bookings cb
        LEFT JOIN commissioners c ON cb.commissioner_id = c.id
        WHERE cb.created_at > CURRENT_DATE - INTERVAL '30 days'
        AND cb.base_price > 0
        ORDER BY cb.created_at DESC
    """)
    
    bookings = cursor.fetchall()
    
    if not bookings:
        print("No bookings found in the last 30 days")
        return
    
    print(f"\nFound {len(bookings)} bookings in the last 30 days:")
    
    for booking in bookings:
        pickup_date = booking['pickup_date']
        base_price = float(booking['base_price'] or 0)
        commission_amount = float(booking['commission_amount'] or 0)
        commission_rate = float(booking['commission_rate'] or 20.0)
        commissioner_name = booking['username'] or f"ID: {booking['commissioner_id']}"
        
        print(f"\nBooking ID: {booking['id']}")
        print(f"  Commissioner: {commissioner_name}")
        print(f"  Pickup Date: {pickup_date}")
        print(f"  Base Price: {base_price}")
        print(f"  Commission Rate: {commission_rate}%")
        print(f"  Commission Amount: {commission_amount}")
        print(f"  Created At: {booking['created_at']}")
        
        # Check if calculation is correct
        if pickup_date:
            pickup_dt = pickup_date if isinstance(pickup_date, datetime) else datetime.strptime(str(pickup_date), '%Y-%m-%d').date()
            
            if pickup_dt > datetime(2026, 4, 1).date():
                expected = base_price * (commission_rate / 100.0)
                rule = "After April 1 (no VAT)"
            else:
                expected = (base_price / 1.23) * 0.15
                rule = "Before April 1 (with VAT)"
            
            print(f"  Expected ({rule}): {expected:.2f}")
            
            if abs(commission_amount - expected) > 0.01:
                print(f"  *** INCORRECT CALCULATION ***")
                print(f"  Difference: {commission_amount - expected:.2f}")
            else:
                print(f"  *** CORRECT CALCULATION ***")
    
    # Also check for any booking with base_price around 75 that has commission of 12.20
    print("\n\nLooking for bookings with base_price ~75 and commission ~12.20...")
    cursor.execute("""
        SELECT cb.id, cb.commissioner_id, c.username, cb.pickup_date, 
               cb.base_price, cb.commission_amount, cb.commission_rate,
               cb.created_at
        FROM commission_bookings cb
        LEFT JOIN commissioners c ON cb.commissioner_id = c.id
        WHERE ABS(cb.base_price - 75.0) < 1.0
        AND ABS(cb.commission_amount - 12.20) < 0.5
        ORDER BY cb.created_at DESC
    """)
    
    matching_bookings = cursor.fetchall()
    
    if matching_bookings:
        print(f"\nFound {len(matching_bookings)} bookings matching the criteria:")
        for booking in matching_bookings:
            print(f"  ID: {booking['id']}, Commissioner: {booking['username']}, Date: {booking['pickup_date']}")
            print(f"    Base: {booking['base_price']}, Commission: {booking['commission_amount']}, Rate: {booking['commission_rate']}%")
    else:
        print("No bookings found with base_price ~75 and commission ~12.20")
    
    conn.close()

if __name__ == "__main__":
    check_all_recent_bookings()
