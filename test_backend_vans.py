#!/usr/bin/env python3
"""
Test if vans pricing is being added to periods in load_prices_from_db
"""
import os
import sys
sys.path.insert(0, '/Users/filipepacheco/CascadeProjects/carscraping')

os.environ['DATABASE_URL'] = open('.env').read().split('DATABASE_URL=')[1].split('\n')[0]

import main

# Force reload of module to get latest changes
import importlib
import current_prices_module
importlib.reload(current_prices_module)
from current_prices_module import load_prices_from_db

print("🧪 Testing load_prices_from_db...")

with main._db_lock:
    conn = main._db_connect()
    try:
        periods, _ = load_prices_from_db(conn, 'Albufeira', 3, 2026)
        
        print(f"\n📋 Períodos retornados: {len(periods)}")
        
        if periods and len(periods) > 0:
            first_period = periods[0]
            prices = first_period['prices']
            
            print(f"📋 Grupos no primeiro período: {list(prices.keys())}")
            print(f"📋 Total de grupos: {len(prices.keys())}")
            print(f"📋 C3 in prices? {'C3' in prices}")
            print(f"📋 C4 in prices? {'C4' in prices}")
            print(f"📋 C5 in prices? {'C5' in prices}")
            
            if 'C3' in prices:
                print(f"\n✅ C3 prices:")
                print(f"  1 day: {prices['C3'].get('1', 'N/A')}")
                print(f"  2 days: {prices['C3'].get('2', 'N/A')}")
                print(f"  3 days: {prices['C3'].get('3', 'N/A')}")
            else:
                print("\n❌ C3 NOT in prices!")
                
            if 'C4' in prices:
                print(f"\n✅ C4 prices:")
                print(f"  1 day: {prices['C4'].get('1', 'N/A')}")
            else:
                print("\n❌ C4 NOT in prices!")
                
            if 'C5' in prices:
                print(f"\n✅ C5 prices:")
                print(f"  1 day: {prices['C5'].get('1', 'N/A')}")
            else:
                print("\n❌ C5 NOT in prices!")
        else:
            print("❌ No periods returned!")
            
    finally:
        conn.close()

print("\n✅ Test complete!")
