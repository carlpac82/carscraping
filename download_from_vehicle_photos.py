#!/usr/bin/env python3
"""
Download vehicle images from vehicle_photos table
"""
import os
import sys
import psycopg2
import httpx
from datetime import datetime

def download_from_vehicle_photos():
    """Download images from vehicle_photos table"""
    try:
        print("[DOWNLOAD] Connecting to database...")
        
        # Database connection
        DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check if vehicle_photos table exists and has data
        cur.execute("""
            SELECT vehicle_name, photo_url 
            FROM vehicle_photos 
            WHERE photo_url IS NOT NULL AND photo_url != ''
            LIMIT 20
        """)
        
        rows = cur.fetchall()
        print(f"[DOWNLOAD] Found {len(rows)} vehicles with photos")
        
        if not rows:
            print("[DOWNLOAD] No vehicles found with photos in vehicle_photos table")
            return 0
        
        # Ensure vehicle_images table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_images (
                vehicle_key TEXT PRIMARY KEY,
                image_data BYTEA NOT NULL,
                content_type TEXT DEFAULT 'image/jpeg',
                source_url TEXT,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        downloaded = 0
        for vehicle_name, photo_url in rows:
            try:
                print(f"[DOWNLOAD] Downloading {vehicle_name} from {photo_url}")
                
                # Download image
                response = httpx.get(photo_url, timeout=15)
                if response.status_code == 200:
                    # Save to vehicle_images table
                    vehicle_key = vehicle_name.lower().strip()
                    
                    cur.execute("""
                        INSERT INTO vehicle_images 
                        (vehicle_key, image_data, content_type, source_url, downloaded_at)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (vehicle_key) DO UPDATE SET
                        image_data = EXCLUDED.image_data,
                        content_type = EXCLUDED.content_type,
                        source_url = EXCLUDED.source_url,
                        downloaded_at = EXCLUDED.downloaded_at
                    """, (vehicle_key, response.content, 'image/jpeg', photo_url, datetime.now()))
                    
                    conn.commit()
                    downloaded += 1
                    print(f"[DOWNLOAD] ✓ Downloaded {vehicle_name}")
                else:
                    print(f"[DOWNLOAD] ✗ Failed to download {vehicle_name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"[DOWNLOAD] ✗ Error downloading {vehicle_name}: {e}")
                continue
        
        cur.close()
        conn.close()
        
        print(f"[DOWNLOAD] Complete! Downloaded {downloaded} images from vehicle_photos")
        return downloaded
        
    except Exception as e:
        print(f"[DOWNLOAD] Error: {e}")
        return 0

if __name__ == "__main__":
    downloaded = download_from_vehicle_photos()
    print(f"\n[RESULT] Downloaded {downloaded} vehicle images from vehicle_photos table")
