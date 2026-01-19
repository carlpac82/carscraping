#!/usr/bin/env python3
"""
Migration script to convert inspection_photos.image_data from BYTEA to TEXT
This allows storing base64 inline data URLs (data:image/png;base64,...) directly
"""

import psycopg2
import base64
import os
import logging

logging.basicConfig(level=logging.INFO)

def migrate_image_data_column():
    """Convert image_data column from BYTEA to TEXT and convert existing data"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    # Fix Railway's postgres:// to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔍 Checking current column type...")
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'inspection_photos' 
            AND column_name = 'image_data'
        """)
        
        result = cursor.fetchone()
        if not result:
            print("❌ Column image_data not found")
            return False
        
        current_type = result[0]
        print(f"📊 Current type: {current_type}")
        
        if current_type == 'text':
            print("✅ Column is already TEXT type")
            return True
        
        # Step 1: Create temporary column
        print("📝 Creating temporary TEXT column...")
        cursor.execute("""
            ALTER TABLE inspection_photos 
            ADD COLUMN image_data_text TEXT
        """)
        conn.commit()
        print("✅ Temporary column created")
        
        # Step 2: Convert existing BYTEA data to base64 TEXT
        print("🔄 Converting existing data from BYTEA to base64 TEXT...")
        cursor.execute("""
            SELECT id, image_data, photo_type 
            FROM inspection_photos 
            WHERE image_data IS NOT NULL
        """)
        
        rows = cursor.fetchall()
        print(f"📊 Found {len(rows)} photos to convert")
        
        converted = 0
        for row_id, image_data, photo_type in rows:
            try:
                if isinstance(image_data, memoryview):
                    image_data = bytes(image_data)
                
                if isinstance(image_data, bytes):
                    # Convert bytes to base64 string with data URL prefix
                    base64_str = base64.b64encode(image_data).decode('utf-8')
                    data_url = f"data:image/png;base64,{base64_str}"
                    
                    cursor.execute("""
                        UPDATE inspection_photos 
                        SET image_data_text = %s 
                        WHERE id = %s
                    """, (data_url, row_id))
                    converted += 1
                    
                    if converted % 10 == 0:
                        print(f"  Converted {converted}/{len(rows)} photos...")
                        
            except Exception as e:
                print(f"⚠️ Error converting photo {row_id} ({photo_type}): {e}")
                continue
        
        conn.commit()
        print(f"✅ Converted {converted} photos to base64 TEXT")
        
        # Step 3: Drop old BYTEA column
        print("🗑️ Dropping old BYTEA column...")
        cursor.execute("""
            ALTER TABLE inspection_photos 
            DROP COLUMN image_data
        """)
        conn.commit()
        print("✅ Old column dropped")
        
        # Step 4: Rename new column to image_data
        print("📝 Renaming new column to image_data...")
        cursor.execute("""
            ALTER TABLE inspection_photos 
            RENAME COLUMN image_data_text TO image_data
        """)
        conn.commit()
        print("✅ Column renamed")
        
        cursor.close()
        conn.close()
        
        print("🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    migrate_image_data_column()
