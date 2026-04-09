#!/usr/bin/env python3
"""
Test manual booking creation in production to verify commission calculation
"""
import requests
import json
from datetime import datetime

def test_production_manual_booking():
    # First, let's check if we can access the commissioner info
    api_base = "https://carscraping.up.railway.app"
    
    print("Testing production manual booking...")
    
    # Test data
    test_booking = {
        "commissioner_id": 157,  # AUTO PRUDENTE
        "pickup_date": "2026-04-09",
        "days": 1,
        "vehicle_group": "ECONOMY",
        "base_price": 75.00,
        "deposit": 300.00,
        "manual_voucher": ""
    }
    
    try:
        # Try to create the booking (this will likely fail without auth)
        response = requests.post(
            f"{api_base}/api/admin/manual-booking",
            json=test_booking,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("Expected: Authorization required")
            
            # Let's check if there's a way to test the calculation directly
            # We'll create a simple test endpoint
            print("\nCreating test endpoint to verify calculation...")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Alternative: Check existing bookings for this commissioner
    print("\nChecking existing bookings for AUTO PRUDENTE (ID: 157)...")
    
    # Get commissioner bookings (this might also require auth)
    try:
        response = requests.get(
            f"{api_base}/api/admin/commissioners/157/bookings",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            bookings = response.json()
            print(f"Found {len(bookings)} bookings")
            
            # Check recent bookings
            for booking in bookings[-5:]:  # Last 5 bookings
                pickup_date = booking.get('pickup_date', '')
                base_price = booking.get('base_price', 0)
                commission_amount = booking.get('commission_amount', 0)
                
                print(f"\nBooking: {booking.get('id')}")
                print(f"  Date: {pickup_date}")
                print(f"  Base Price: {base_price}")
                print(f"  Commission: {commission_amount}")
                
                # Check if calculation is correct
                if pickup_date > '2026-04-01':
                    expected = base_price * 0.20
                    print(f"  Expected (20%): {expected}")
                else:
                    expected = (base_price / 1.23) * 0.15
                    print(f"  Expected (15% with VAT): {expected}")
                    
                if abs(commission_amount - expected) > 0.01:
                    print(f"  *** INCORRECT CALCULATION ***")
        else:
            print(f"Failed to get bookings: {response.status_code}")
            
    except Exception as e:
        print(f"Error checking bookings: {e}")

if __name__ == "__main__":
    test_production_manual_booking()
