#!/usr/bin/env python3
"""
Download vehicle images for PDF voucher groups
"""
import os
import sys
import psycopg2
import httpx
from datetime import datetime, timedelta
import time

# Vehicle groups and their CarJet model names
group_models = {
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

def download_vehicle_images():
    """Download images from CarJet and save to database"""
    try:
        # Import CarJet scraper
        sys.path.append('/Users/filipepacheco/CascadeProjects/carscraping')
        from carjet_direct import scrape_carjet_direct
        
        print("[DOWNLOAD] Starting vehicle image download...")
        
        # Database connection
        DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Ensure table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_images (
                vehicle_key TEXT PRIMARY KEY,
                image_data BYTEA NOT NULL,
                content_type TEXT DEFAULT 'image/jpeg',
                source_url TEXT,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Scrape CarJet
        start_date = datetime.now() + timedelta(days=5)
        end_date = start_date + timedelta(days=1)
        
        print(f"[DOWNLOAD] Scraping CarJet for {start_date.strftime('%d/%m/%Y')}...")
        results = scrape_carjet_direct("Faro", start_date, end_date, quick=1)
        
        downloaded = 0
        for item in results:
            car_name = item.get('car', '').strip().lower()
            photo_url = item.get('photo', '')
            
            if not photo_url:
                continue
                
            # Check if this car matches any group model
            for group, model in group_models.items():
                if model in car_name or car_name in model:
                    try:
                        print(f"[DOWNLOAD] Found {model} for group {group}: {car_name}")
                        
                        # Download image
                        response = httpx.get(photo_url, timeout=15)
                        if response.status_code == 200:
                            # Save to database
                            cur.execute("""
                                INSERT OR REPLACE INTO vehicle_images 
                                (vehicle_key, image_data, content_type, source_url, downloaded_at)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (model, response.content, 'image/jpeg', photo_url, datetime.now()))
                            
                            conn.commit()
                            downloaded += 1
                            print(f"[DOWNLOAD] ✓ Downloaded {model} for group {group}")
                            break
                        else:
                            print(f"[DOWNLOAD] ✗ Failed to download {model}: HTTP {response.status_code}")
                            
                    except Exception as e:
                        print(f"[DOWNLOAD] ✗ Error downloading {car_name}: {e}")
                        continue
        
        cur.close()
        conn.close()
        
        print(f"[DOWNLOAD] Complete! Downloaded {downloaded} images")
        return downloaded
        
    except Exception as e:
        print(f"[DOWNLOAD] Error: {e}")
        return 0

if __name__ == "__main__":
    downloaded = download_vehicle_images()
    print(f"\n[RESULT] Downloaded {downloaded} vehicle images for PDF vouchers")
