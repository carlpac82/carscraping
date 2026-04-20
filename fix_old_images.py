#!/usr/bin/env python3
"""
Script para corrigir imagens antigas com padding incorreto na base de dados.
Executa uma vez para corrigir todos os registos antigos.
"""

import os
import sys
import psycopg2
import base64
import binascii

def fix_base64_padding(data):
    """Fix base64 padding if needed"""
    if not data:
        return data
    
    # Remove whitespace and existing padding
    data = data.strip().replace('\n', '').replace('\r', '').replace(' ', '').rstrip('=')
    
    # Add correct padding
    padding_needed = (4 - len(data) % 4) % 4
    if padding_needed > 0:
        data += '=' * padding_needed
    
    return data

def main():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        sys.exit(1)
    
    print("🔧 Connecting to database...")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Get all photos with invalid base64 (not starting with data:image and not bytes)
    print("🔍 Finding photos with invalid base64...")
    cursor.execute("""
        SELECT id, photo_type, LENGTH(image_data) as len,
               LEFT(image_data, 50) as preview
        FROM inspection_photos
        WHERE image_data IS NOT NULL
          AND image_data NOT LIKE 'data:image%'
          AND image_data NOT LIKE '\\x%'
        ORDER BY id
    """)
    
    photos = cursor.fetchall()
    print(f"📊 Found {len(photos)} photos to check")
    
    fixed_count = 0
    error_count = 0
    
    for photo_id, photo_type, data_len, preview in photos:
        # Check if length is valid (multiple of 4)
        if data_len % 4 != 0:
            print(f"\n🔧 Fixing photo ID {photo_id} ({photo_type}): len={data_len} (invalid)")
            
            try:
                # Get full data
                cursor.execute("SELECT image_data FROM inspection_photos WHERE id = %s", (photo_id,))
                image_data = cursor.fetchone()[0]
                
                # Fix padding
                fixed_data = fix_base64_padding(image_data)
                
                # Verify it's valid base64
                try:
                    base64.b64decode(fixed_data)
                    
                    # Add data URL prefix
                    fixed_data_url = f"data:image/jpeg;base64,{fixed_data}"
                    
                    # Update database
                    cursor.execute("""
                        UPDATE inspection_photos 
                        SET image_data = %s 
                        WHERE id = %s
                    """, (fixed_data_url, photo_id))
                    
                    fixed_count += 1
                    print(f"   ✅ Fixed: {data_len} -> {len(fixed_data)} chars, added data URL prefix")
                    
                except Exception as decode_error:
                    print(f"   ⚠️ Still invalid after padding fix: {decode_error}")
                    error_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error fixing photo {photo_id}: {e}")
                error_count += 1
        else:
            # Valid length but missing data URL prefix - add it
            try:
                cursor.execute("SELECT image_data FROM inspection_photos WHERE id = %s", (photo_id,))
                image_data = cursor.fetchone()[0]
                
                # Verify it's valid base64
                base64.b64decode(image_data)
                
                # Add data URL prefix
                fixed_data_url = f"data:image/jpeg;base64,{image_data}"
                
                cursor.execute("""
                    UPDATE inspection_photos 
                    SET image_data = %s 
                    WHERE id = %s
                """, (fixed_data_url, photo_id))
                
                fixed_count += 1
                print(f"✅ Added data URL prefix to photo ID {photo_id} ({photo_type})")
                
            except Exception as e:
                print(f"⚠️ Photo ID {photo_id} has valid length but invalid base64: {e}")
                error_count += 1
    
    # Commit changes
    conn.commit()
    
    print(f"\n{'='*60}")
    print(f"✅ Fixed {fixed_count} photos")
    print(f"❌ Errors: {error_count}")
    print(f"{'='*60}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
