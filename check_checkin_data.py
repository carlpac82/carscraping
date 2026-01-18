import psycopg2
import json

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Get latest checkin
cursor.execute("""
    SELECT inspection_number, damage_count, has_damage
    FROM vehicle_inspections 
    WHERE inspection_type = 'checkin' 
    ORDER BY created_at DESC 
    LIMIT 1
""")

row = cursor.fetchone()
if row:
    print(f"Inspection: {row[0]}")
    print(f"Damage count: {row[1]}")
    print(f"Has damage: {row[2]}")
    
    # Get inspection ID
    cursor.execute("""
        SELECT id FROM vehicle_inspections WHERE inspection_number = %s
    """, (row[0],))
    
    inspection_id_row = cursor.fetchone()
    if not inspection_id_row:
        print("Inspection ID not found")
    else:
        inspection_id = inspection_id_row[0]
        print(f"Inspection ID: {inspection_id}")
        
        # Check photos
        cursor.execute("""
            SELECT photo_type, LENGTH(image_data) as size
            FROM inspection_photos 
            WHERE inspection_id = %s
            ORDER BY photo_type
        """, (inspection_id,))
    
    photos = cursor.fetchall()
    print(f"\nPhotos ({len(photos)}):")
    for photo in photos:
        print(f"  - {photo[0]}: {photo[1]} bytes")

cursor.close()
conn.close()
