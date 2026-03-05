#!/usr/bin/env python3
"""
Script to copy inspection data from ID 363 (AS-78-RH) to ID 384 (AT-28-NX)
for RA 6932
"""
import os
import psycopg2

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    exit(1)

print(f"🔗 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    # Get source inspection data (363)
    print("📋 Fetching source inspection data (ID 363)...")
    cur.execute("""
        SELECT odometer_reading, fuel_level, created_at, inspector_name, inspector_notes
        FROM vehicle_inspections
        WHERE id = 363
    """)
    source_data = cur.fetchone()
    
    if not source_data:
        print("❌ Source inspection 363 not found")
        exit(1)
    
    odometer, fuel, created_at, inspector, notes = source_data
    print(f"✅ Source data: odometer={odometer}, fuel={fuel}, inspector={inspector}")
    
    # Get source photos
    print("📸 Fetching source photos...")
    cur.execute("""
        SELECT photo_type, photo_order, image_data, image_filename
        FROM inspection_photos
        WHERE inspection_id = 363
        ORDER BY photo_order
    """)
    source_photos = cur.fetchall()
    print(f"✅ Found {len(source_photos)} photos")
    
    # Delete existing photos from inspection 384
    print("🗑️ Deleting existing photos from inspection 384...")
    cur.execute("DELETE FROM inspection_photos WHERE inspection_id = 384")
    deleted_count = cur.rowcount
    print(f"✅ Deleted {deleted_count} old photos")
    
    # Copy photos to inspection 384
    print("📸 Copying photos to inspection 384...")
    inserted_count = 0
    for photo in source_photos:
        cur.execute("""
            INSERT INTO inspection_photos 
            (inspection_id, photo_type, photo_order, image_data, image_filename)
            VALUES (%s, %s, %s, %s, %s)
        """, (384, photo[0], photo[1], photo[2], photo[3]))
        inserted_count += 1
    print(f"✅ Inserted {inserted_count} new photos")
    
    # Update inspection 384 with ALL data from 363
    print("📝 Updating inspection 384 with source data...")
    cur.execute("""
        UPDATE vehicle_inspections
        SET odometer_reading = %s,
            fuel_level = %s,
            created_at = %s,
            inspector_name = %s,
            inspector_notes = %s
        WHERE id = 384
    """, (odometer, fuel, created_at, inspector, notes))
    print(f"✅ Updated inspection 384")
    
    # Commit changes
    conn.commit()
    print("\n✅ SUCCESS! All data copied from inspection 363 to 384")
    print(f"   - Deleted {deleted_count} old photos")
    print(f"   - Inserted {inserted_count} new photos")
    print(f"   - Updated inspection metadata")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ ERROR: {e}")
    raise
finally:
    cur.close()
    conn.close()
