#!/usr/bin/env python3
"""
Test commission calculation logic directly
"""
import sqlite3
from datetime import datetime, date

def test_commission_calculation():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Get commissioner info
    cursor.execute("SELECT id, username, commission_rate FROM commissioners WHERE id = 157")
    commissioner = cursor.fetchone()
    
    if not commissioner:
        print("Commissioner not found!")
        return
    
    commissioner_id, username, commission_rate = commissioner
    print(f"Commissioner: {username} (ID: {commissioner_id})")
    print(f"Commission rate: {commission_rate}%")
    
    # Test calculation for dates
    test_cases = [
        ("2026-03-31", 75.00),  # Before April 1
        ("2026-04-01", 75.00),  # April 1
        ("2026-04-09", 75.00),  # After April 1
    ]
    
    cutoff_date = date(2026, 4, 1)
    
    for pickup_date_str, base_price in test_cases:
        pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
        
        if pickup_date > cutoff_date:
            # After April 1, 2026: no VAT deduction
            commission_amount = base_price * (commission_rate / 100.0)
            rule = "After April 1 (no VAT)"
        else:
            # Before April 1, 2026: with VAT deduction using 15% rate
            commission_amount = (base_price / 1.23) * 0.15
            rule = "Before April 1 (with VAT)"
        
        print(f"\nDate: {pickup_date_str}")
        print(f"Base price: {base_price}")
        print(f"Rule: {rule}")
        print(f"Commission: {commission_amount:.2f} euros")
    
    # Now test with actual database insert
    print("\n--- Testing Database Insert ---")
    pickup_date = "2026-04-09"
    base_price = 75.00
    days = 1
    vehicle_group = "ECONOMY"
    deposit = 300.00
    
    # Calculate commission
    pickup_dt = datetime.strptime(pickup_date, '%Y-%m-%d')
    april_1st_2026 = datetime(2026, 4, 1)
    
    if pickup_dt > april_1st_2026:
        commission_amount = base_price * (commission_rate / 100.0)
        print(f"Calculated commission: {commission_amount}")
    else:
        commission_amount = (base_price / 1.23) * 0.15
        print(f"Calculated commission: {commission_amount}")
    
    # Insert test booking
    cursor.execute("""
        INSERT INTO commission_bookings (
            commissioner_id, voucher_number, client_name, client_email, client_phone,
            pickup_date, pickup_time, dropoff_date, dropoff_time,
            pickup_location, dropoff_location, vehicle_group, extras,
            price, base_price, deposit, status, commission_rate, commission_amount,
            created_at, updated_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        )
    """, (
        commissioner_id, None, '', '', '',
        pickup_date, '00:00', pickup_date, '00:00',
        '', '', vehicle_group, '[]',
        base_price, base_price, deposit, 'confirmed', commission_rate, commission_amount
    ))
    
    booking_id = cursor.lastrowid
    conn.commit()
    
    # Verify the insert
    cursor.execute("""
        SELECT id, commission_amount, base_price, commission_rate 
        FROM commission_bookings 
        WHERE id = ?
    """, (booking_id,))
    
    result = cursor.fetchone()
    if result:
        print(f"\nBooking ID: {result[0]}")
        print(f"Stored commission: {result[1]}")
        print(f"Base price: {result[2]}")
        print(f"Commission rate: {result[3]}")
        
        # Clean up test booking
        cursor.execute("DELETE FROM commission_bookings WHERE id = ?", (booking_id,))
        conn.commit()
        print("Test booking cleaned up")
    
    conn.close()

if __name__ == "__main__":
    test_commission_calculation()
