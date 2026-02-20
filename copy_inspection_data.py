#!/usr/bin/env python3
"""
Script to copy croqui and photos from RA 06850 check-in inspection to RA 06876-09 latest inspection
Also updates inspector name to "Lina Prudente" and time to 15:55
"""

import psycopg2
import os
from datetime import datetime

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')

def copy_inspection_data():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # 1. Find source inspection (RA 06850 check-in)
        cur.execute("""
            SELECT id, inspection_number, damage_croqui_base64
            FROM vehicle_inspections
            WHERE contract_number LIKE '06850%'
              AND inspection_type = 'checkin'
              AND COALESCE(status, '') != 'replaced'
            ORDER BY created_at DESC
            LIMIT 1
        """)
        source_inspection = cur.fetchone()
        
        if not source_inspection:
            print("❌ Source inspection (RA 06850 check-in) not found")
            return
        
        source_id, source_number, source_croqui = source_inspection
        print(f"✅ Found source inspection: {source_number} (ID: {source_id})")
        
        # 2. Find target inspection (RA 06876-09 latest)
        cur.execute("""
            SELECT id, inspection_number
            FROM vehicle_inspections
            WHERE contract_number LIKE '06876%'
            ORDER BY created_at DESC
            LIMIT 1
        """)
        target_inspection = cur.fetchone()
        
        if not target_inspection:
            print("❌ Target inspection (RA 06876-09) not found")
            return
        
        target_id, target_number = target_inspection
        print(f"✅ Found target inspection: {target_number} (ID: {target_id})")
        
        # 3. Copy croqui
        if source_croqui:
            cur.execute("""
                UPDATE vehicle_inspections
                SET damage_croqui_base64 = %s
                WHERE id = %s
            """, (source_croqui, target_id))
            print(f"✅ Copied croqui from {source_number} to {target_number}")
        else:
            print("⚠️ No croqui found in source inspection")
        
        # 4. Copy photos
        cur.execute("""
            SELECT photo_base64, photo_type, photo_order, damage_id
            FROM inspection_photos
            WHERE inspection_id = %s
            ORDER BY photo_order
        """, (source_id,))
        photos = cur.fetchall()
        
        if photos:
            # Delete existing photos from target
            cur.execute("DELETE FROM inspection_photos WHERE inspection_id = %s", (target_id,))
            print(f"🗑️ Deleted existing photos from target inspection")
            
            # Insert copied photos
            for photo in photos:
                cur.execute("""
                    INSERT INTO inspection_photos (inspection_id, photo_base64, photo_type, photo_order, damage_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (target_id, photo[0], photo[1], photo[2], photo[3]))
            
            print(f"✅ Copied {len(photos)} photos from {source_number} to {target_number}")
        else:
            print("⚠️ No photos found in source inspection")
        
        # 5. Update inspector name and time
        cur.execute("""
            UPDATE vehicle_inspections
            SET inspector_name = 'Lina Prudente',
                created_at = DATE_TRUNC('day', created_at) + INTERVAL '15 hours 55 minutes'
            WHERE id = %s
        """, (target_id,))
        print(f"✅ Updated inspector to 'Lina Prudente' and time to 15:55")
        
        # 6. Update photo count
        cur.execute("""
            UPDATE vehicle_inspections
            SET photo_count = (SELECT COUNT(*) FROM inspection_photos WHERE inspection_id = %s)
            WHERE id = %s
        """, (target_id, target_id))
        
        conn.commit()
        print(f"\n✅ SUCCESS: All data copied from RA 06850 to RA 06876-09")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    copy_inspection_data()
