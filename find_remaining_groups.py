#!/usr/bin/env python3
"""
Find exact names for remaining groups
"""
import os
import psycopg2

def find_remaining_groups():
    """Find exact names for groups A, B, E1, G, J1, J2, L1, L2"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Get all vehicle names
        cur.execute("SELECT vehicle_key FROM vehicle_images ORDER BY vehicle_key")
        all_vehicles = [row[0] for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        # Groups to find
        groups_to_find = {
            'A': ['kia', 'picanto'],
            'B': ['fiat', 'panda'],
            'E1': ['hyundai', 'i10'],
            'G': ['fiat', '500'],
            'J1': ['peugeot', '2008'],
            'J2': ['peugeot', '308'],
            'L1': ['citroen', 'aircross'],
            'L2': ['peugeot', '308']
        }
        
        print("[SEARCH] Finding exact names for remaining groups:")
        print("=" * 60)
        
        found_mapping = {}
        
        for group, keywords in groups_to_find.items():
            matches = []
            for vehicle in all_vehicles:
                vehicle_lower = vehicle.lower()
                # Check if all keywords are in the vehicle name
                if all(keyword.lower() in vehicle_lower for keyword in keywords):
                    matches.append(vehicle)
            
            if matches:
                # Use the first/best match
                found_mapping[group] = matches[0]
                print(f"✅ {group}: {keywords} -> '{matches[0]}'")
                if len(matches) > 1:
                    print(f"   Other options: {matches[1:3]}")
            else:
                print(f"❌ {group}: {keywords} -> NO MATCH FOUND")
                # Try partial matches
                for vehicle in all_vehicles:
                    vehicle_lower = vehicle.lower()
                    if any(keyword.lower() in vehicle_lower for keyword in keywords):
                        print(f"   Partial match: '{vehicle}'")
        
        print("\n[FINAL MAPPING] Update vehicle_api_names with:")
        print("vehicle_api_names = {")
        
        # Add already working groups
        working_groups = {
            'D': 'seat ibiza',
            'E2': 'citroen c3',
            'F': 'seat arona',
            'M1': 'dacia jogger',
            'M2': 'citroen c4',
            'N': 'toyota proace'
        }
        
        for group, name in working_groups.items():
            print(f"    '{group}': '{name}',  # ✅ WORKING")
        
        # Add newly found groups
        for group, name in found_mapping.items():
            print(f"    '{group}': '{name}',  # ✅ FOUND")
        
        print("}")
        
        return found_mapping
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return {}

if __name__ == "__main__":
    find_remaining_groups()
