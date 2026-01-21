#!/usr/bin/env python3
"""
Migration script to rename inspection_type values in the database.

OLD (confusing):
- 'checkout' in DB = CHECK-IN (entrega)
- 'checkin' in DB = CHECK-OUT (recolha)

NEW (correct):
- 'checkin' in DB = CHECK-IN (entrega)
- 'checkout' in DB = CHECK-OUT (recolha)

This script:
1. Renames 'checkout' -> 'checkin_temp'
2. Renames 'checkin' -> 'checkout_temp'
3. Renames 'checkin_temp' -> 'checkin'
4. Renames 'checkout_temp' -> 'checkout'
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def migrate_inspection_types():
    """Migrate inspection_type values in the database."""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check current counts
        print("\n📊 Current inspection_type counts:")
        cursor.execute("""
            SELECT inspection_type, COUNT(*) as count
            FROM vehicle_inspections
            GROUP BY inspection_type
            ORDER BY inspection_type
        """)
        for row in cursor.fetchall():
            print(f"   {row['inspection_type']}: {row['count']}")
        
        # Start transaction
        print("\n🔄 Starting migration...")
        
        # Step 1: Rename 'checkout' -> 'checkin_temp'
        print("   Step 1: Renaming 'checkout' -> 'checkin_temp'...")
        cursor.execute("""
            UPDATE vehicle_inspections
            SET inspection_type = 'checkin_temp'
            WHERE inspection_type = 'checkout'
        """)
        rows_updated = cursor.rowcount
        print(f"   ✅ Updated {rows_updated} rows")
        
        # Step 2: Rename 'checkin' -> 'checkout_temp'
        print("   Step 2: Renaming 'checkin' -> 'checkout_temp'...")
        cursor.execute("""
            UPDATE vehicle_inspections
            SET inspection_type = 'checkout_temp'
            WHERE inspection_type = 'checkin'
        """)
        rows_updated = cursor.rowcount
        print(f"   ✅ Updated {rows_updated} rows")
        
        # Step 3: Rename 'checkin_temp' -> 'checkin'
        print("   Step 3: Renaming 'checkin_temp' -> 'checkin'...")
        cursor.execute("""
            UPDATE vehicle_inspections
            SET inspection_type = 'checkin'
            WHERE inspection_type = 'checkin_temp'
        """)
        rows_updated = cursor.rowcount
        print(f"   ✅ Updated {rows_updated} rows")
        
        # Step 4: Rename 'checkout_temp' -> 'checkout'
        print("   Step 4: Renaming 'checkout_temp' -> 'checkout'...")
        cursor.execute("""
            UPDATE vehicle_inspections
            SET inspection_type = 'checkout'
            WHERE inspection_type = 'checkout_temp'
        """)
        rows_updated = cursor.rowcount
        print(f"   ✅ Updated {rows_updated} rows")
        
        # Commit transaction
        conn.commit()
        print("\n✅ Migration committed successfully!")
        
        # Check new counts
        print("\n📊 New inspection_type counts:")
        cursor.execute("""
            SELECT inspection_type, COUNT(*) as count
            FROM vehicle_inspections
            GROUP BY inspection_type
            ORDER BY inspection_type
        """)
        for row in cursor.fetchall():
            print(f"   {row['inspection_type']}: {row['count']}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        print("\nNOW:")
        print("   'checkin' in DB = CHECK-IN (entrega)")
        print("   'checkout' in DB = CHECK-OUT (recolha)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    migrate_inspection_types()
