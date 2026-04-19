#!/usr/bin/env python3
"""
Fix base64 padding issues in inspection_photos table
"""
import psycopg2
import os
import base64
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv('DATABASE_URL')

def fix_base64_padding(data):
    """Fix base64 padding by adding missing '=' characters"""
    if not data:
        return data
    
    # Remove data URI prefix if present
    if 'data:image' in data:
        parts = data.split(',', 1)
        if len(parts) == 2:
            prefix = parts[0] + ','
            b64_data = parts[1]
        else:
            return data
    else:
        prefix = ''
        b64_data = data
    
    # Calculate missing padding
    missing_padding = len(b64_data) % 4
    if missing_padding:
        b64_data += '=' * (4 - missing_padding)
    
    # Verify it's valid base64 now
    try:
        base64.b64decode(b64_data)
        return prefix + b64_data
    except Exception as e:
        print(f"  ⚠️  Still invalid after padding fix: {str(e)[:100]}")
        return None

def main():
    print("🔧 Fixing base64 padding in inspection_photos...")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Get all photos with image_data
    cursor.execute("""
        SELECT id, photo_type, LENGTH(image_data::text) as data_len
        FROM inspection_photos 
        WHERE image_data IS NOT NULL
        ORDER BY id
    """)
    
    photos = cursor.fetchall()
    print(f"\n📊 Found {len(photos)} photos to check")
    
    fixed_count = 0
    error_count = 0
    
    for photo_id, photo_type, data_len in photos:
        # Get the actual data
        cursor.execute("SELECT image_data FROM inspection_photos WHERE id = %s", (photo_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            continue
            
        image_data = result[0]
        
        # Check if it's a string (base64) or bytea (hex)
        if not isinstance(image_data, str):
            # It's bytea, skip
            continue
        
        # Check if it starts with \x (hex format)
        if image_data.startswith('\\x'):
            # It's hex format, skip
            continue
        
        # Try to decode as-is
        try:
            if 'data:image' in image_data:
                b64_part = image_data.split(',', 1)[1] if ',' in image_data else image_data
            else:
                b64_part = image_data
            
            base64.b64decode(b64_part)
            # Already valid, skip
            continue
            
        except Exception as e:
            error_msg = str(e)
            
            # Try to fix padding
            fixed_data = fix_base64_padding(image_data)
            
            if fixed_data and fixed_data != image_data:
                # Update in database
                try:
                    cursor.execute(
                        "UPDATE inspection_photos SET image_data = %s WHERE id = %s",
                        (fixed_data, photo_id)
                    )
                    conn.commit()
                    print(f"✅ Fixed photo {photo_id} ({photo_type})")
                    fixed_count += 1
                except Exception as update_error:
                    print(f"❌ Error updating photo {photo_id}: {update_error}")
                    conn.rollback()
                    error_count += 1
            else:
                print(f"⚠️  Could not fix photo {photo_id} ({photo_type}): {error_msg[:80]}")
                error_count += 1
    
    cursor.close()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"✅ Fixed: {fixed_count} photos")
    print(f"❌ Errors: {error_count} photos")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
