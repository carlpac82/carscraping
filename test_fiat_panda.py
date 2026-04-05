#!/usr/bin/env python3
"""
Test if fiat panda exists in database
"""
import os
import psycopg2

def test_fiat_panda():
    """Test if fiat panda exists in vehicle_images"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Test exact match
        cur.execute("SELECT vehicle_key, content_type FROM vehicle_images WHERE vehicle_key = %s", ('fiat panda',))
        exact_match = cur.fetchone()
        
        print(f"[TEST] Searching for 'fiat panda':")
        if exact_match:
            print(f"✅ EXACT MATCH FOUND: '{exact_match[0]}' - {exact_match[1]}")
        else:
            print(f"❌ No exact match found")
        
        # Test partial matches
        cur.execute("SELECT vehicle_key FROM vehicle_images WHERE vehicle_key ILIKE %s", ('%fiat%panda%',))
        partial_matches = cur.fetchall()
        
        print(f"\n[TEST] Partial matches for 'fiat panda':")
        if partial_matches:
            for match in partial_matches:
                print(f"  📝 '{match[0]}'")
        else:
            print("❌ No partial matches found")
        
        # Test all fiat vehicles
        cur.execute("SELECT vehicle_key FROM vehicle_images WHERE vehicle_key ILIKE %s ORDER BY vehicle_key", ('fiat%',))
        fiat_vehicles = cur.fetchall()
        
        print(f"\n[TEST] All FIAT vehicles in database:")
        if fiat_vehicles:
            for vehicle in fiat_vehicles:
                print(f"  🚗 '{vehicle[0]}'")
        else:
            print("❌ No FIAT vehicles found")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    test_fiat_panda()
