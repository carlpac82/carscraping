#!/usr/bin/env python3
"""
Check exact vehicle names in database and fix mapping
"""
import os
import psycopg2

def check_exact_names():
    """Check exact names in vehicle_images table"""
    try:
        print("[CHECK] Connecting to database...")
        
        DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Get all vehicle names
        cur.execute("""
            SELECT vehicle_key, content_type, downloaded_at 
            FROM vehicle_images 
            ORDER BY vehicle_key
        """)
        
        rows = cur.fetchall()
        print(f"\n[CHECK] Found {len(rows)} vehicles in database:")
        print("=" * 60)
        
        for row in rows:
            print(f"  '{row[0]}' - {row[1]} - {row[2]}")
        
        cur.close()
        conn.close()
        
        return rows
        
    except Exception as e:
        print(f"[CHECK] Error: {e}")
        return []

if __name__ == "__main__":
    vehicles = check_exact_names()
    
    print(f"\n[RESULT] Total vehicles: {len(vehicles)}")
    print("\n[SUGGESTED MAPPING] Update vehicle_api_names in voucher_api.py:")
    print("vehicle_api_names = {")
    
    # Group mapping suggestions
    group_mapping = {
        'A': 'kia picanto',
        'B': 'fiat panda', 
        'D': 'seat ibiza',
        'E1': 'hyundai i10',
        'E2': 'citroen c3',
        'F': 'seat arona',
        'G': 'fiat 500',
        'J1': 'peugeot 2008',
        'J2': 'peugeot 308 sw',
        'L1': 'citroen c3 aircross',
        'L2': 'peugeot 308 sw',
        'M1': 'dacia jogger',
        'M2': 'citroen c4 picasso',
        'N': 'toyota proace'
    }
    
    for group, model in group_mapping.items():
        # Find exact match in database
        exact_match = None
        for vehicle_key, _, _ in vehicles:
            if model.lower() in vehicle_key.lower() or vehicle_key.lower() in model.lower():
                exact_match = vehicle_key
                break
        
        if exact_match:
            print(f"    '{group}': '{exact_match}',")
        else:
            print(f"    '{group}': '{model}',  # NO MATCH FOUND")
    
    print("}")
