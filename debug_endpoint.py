#!/usr/bin/env python3
"""
Test endpoint behavior
"""
import os
import psycopg2

def test_endpoint_behavior():
    """Test exactly what the endpoint is searching for"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Simulate endpoint behavior
        vehicle_name = "fiat panda"
        vehicle_key = vehicle_name.lower().strip()
        
        print(f"[TEST] Endpoint receives: '{vehicle_name}'")
        print(f"[TEST] Endpoint searches for: '{vehicle_key}'")
        
        # Test exact query like endpoint does
        cur.execute("SELECT image_data, content_type FROM vehicle_images WHERE vehicle_key = %s", (vehicle_key,))
        row = cur.fetchone()
        
        if row:
            print(f"✅ FOUND: image_data ({len(row[0])} bytes), {row[1]}")
        else:
            print(f"❌ NOT FOUND with exact query")
            
            # Try to debug - show similar keys
            cur.execute("SELECT vehicle_key FROM vehicle_images WHERE vehicle_key ILIKE %s", ('%panda%',))
            similar = cur.fetchall()
            print(f"[DEBUG] Similar keys:")
            for s in similar:
                print(f"  '{s[0]}'")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    test_endpoint_behavior()
