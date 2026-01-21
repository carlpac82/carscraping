#!/usr/bin/env python3
"""
Script to REVERT the incorrect database migration
Reverts: check_in → checkout, check_out → check_in
"""

import psycopg2
import os
from urllib.parse import urlparse

def get_db_connection():
    """Get database connection from DATABASE_URL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise Exception("DATABASE_URL not set")
    
    # Parse URL
    result = urlparse(database_url)
    
    return psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

def main():
    print("="*60)
    print("DATABASE REVERT: Restore original inspection types")
    print("="*60)
    print("\nREVERTING incorrect migration:")
    print("  'check_in' → 'checkout' (restore)")
    print("  'check_out' → 'check_in' (restore)")
    
    response = input("\nProceed with revert? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Show current state
        print("\n" + "="*60)
        print("BEFORE REVERT:")
        print("="*60)
        cursor.execute("""
            SELECT inspection_type, COUNT(*) as count
            FROM vehicle_inspections
            GROUP BY inspection_type
            ORDER BY inspection_type
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} records")
        
        # Step 1: check_in → TEMP_DELIVERY
        print("\nStep 1: Renaming 'check_in' to 'TEMP_DELIVERY'...")
        cursor.execute("""
            UPDATE vehicle_inspections 
            SET inspection_type = 'TEMP_DELIVERY'
            WHERE inspection_type = 'check_in'
        """)
        print(f"  ✓ Updated {cursor.rowcount} records")
        
        # Step 2: check_out → TEMP_PICKUP
        print("\nStep 2: Renaming 'check_out' to 'TEMP_PICKUP'...")
        cursor.execute("""
            UPDATE vehicle_inspections 
            SET inspection_type = 'TEMP_PICKUP'
            WHERE inspection_type = 'check_out'
        """)
        print(f"  ✓ Updated {cursor.rowcount} records")
        
        # Step 3: TEMP_DELIVERY → checkout
        print("\nStep 3: Renaming 'TEMP_DELIVERY' to 'checkout'...")
        cursor.execute("""
            UPDATE vehicle_inspections 
            SET inspection_type = 'checkout'
            WHERE inspection_type = 'TEMP_DELIVERY'
        """)
        print(f"  ✓ Updated {cursor.rowcount} records")
        
        # Step 4: TEMP_PICKUP → check_in
        print("\nStep 4: Renaming 'TEMP_PICKUP' to 'check_in'...")
        cursor.execute("""
            UPDATE vehicle_inspections 
            SET inspection_type = 'check_in'
            WHERE inspection_type = 'TEMP_PICKUP'
        """)
        print(f"  ✓ Updated {cursor.rowcount} records")
        
        # Commit changes
        conn.commit()
        
        # Show final state
        print("\n" + "="*60)
        print("AFTER REVERT:")
        print("="*60)
        cursor.execute("""
            SELECT inspection_type, COUNT(*) as count
            FROM vehicle_inspections
            GROUP BY inspection_type
            ORDER BY inspection_type
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} records")
        
        print("\n" + "="*60)
        print("REVERT COMPLETE!")
        print("="*60)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nRolling back changes...")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

if __name__ == '__main__':
    main()
