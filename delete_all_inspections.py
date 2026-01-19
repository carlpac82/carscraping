#!/usr/bin/env python3
"""
Temporary script to delete all inspections from database
"""
import os
import sys

# Add parent directory to path to import from main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import _db_connect, _is_postgresql_connection
import logging

logging.basicConfig(level=logging.INFO)

def delete_all_inspections():
    """Delete all inspections and photos from database"""
    try:
        conn = _db_connect()
        is_postgres = _is_postgresql_connection(conn)
        
        if is_postgres:
            with conn.cursor() as cur:
                # Delete all photos first (foreign key)
                cur.execute("DELETE FROM inspection_photos")
                photos_deleted = cur.rowcount
                print(f"🗑️ Deleted {photos_deleted} inspection photos")
                
                # Delete all inspections
                cur.execute("DELETE FROM vehicle_inspections")
                inspections_deleted = cur.rowcount
                print(f"🗑️ Deleted {inspections_deleted} vehicle inspections")
                
                # Reset inspection_completed flag in rental_agreements
                cur.execute("UPDATE rental_agreements SET inspection_completed = FALSE, inspection_id = NULL")
                ras_updated = cur.rowcount
                print(f"🔄 Reset {ras_updated} rental agreements")
                
            conn.commit()
        else:
            # Delete all photos first (foreign key)
            conn.execute("DELETE FROM inspection_photos")
            photos_deleted = conn.total_changes
            
            # Delete all inspections
            conn.execute("DELETE FROM vehicle_inspections")
            inspections_deleted = conn.total_changes - photos_deleted
            
            conn.commit()
            print(f"🗑️ Deleted {photos_deleted} photos and {inspections_deleted} inspections")
        
        conn.close()
        
        print(f"✅ Successfully deleted {inspections_deleted} inspections and {photos_deleted} photos")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting inspections: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("⚠️  WARNING: This will delete ALL inspections from the database!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() == "yes":
        success = delete_all_inspections()
        sys.exit(0 if success else 1)
    else:
        print("❌ Operation cancelled")
        sys.exit(1)
