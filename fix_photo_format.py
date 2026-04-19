#!/usr/bin/env python3
"""
Fix photo format: Convert hex strings to proper base64
"""

import os
import psycopg2
import base64
import binascii
from PIL import Image
import io

def fix_photo_format():
    try:
        # Connect to database
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("ERROR: DATABASE_URL not found")
            return
        
        print("Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get all photos
        cursor.execute('SELECT id, image_data FROM inspection_photos WHERE image_data IS NOT NULL')
        photos = cursor.fetchall()
        
        print(f"Found {len(photos)} photos to fix...")
        
        fixed_count = 0
        png_count = 0
        jpeg_count = 0
        
        for photo_id, image_data in photos:
            try:
                if not image_data:
                    continue
                
                # Check if it's hex string (starts with \xff or \x89)
                if isinstance(image_data, str) and image_data.startswith('\\x'):
                    # Convert hex string to bytes
                    try:
                        # Remove \x prefix and convert hex to bytes
                        hex_data = image_data[2:]  # Remove \x
                        image_bytes = binascii.unhexlify(hex_data)
                        
                        # Detect image format
                        if image_bytes.startswith(b'\x89PNG'):
                            # PNG - preserve transparency
                            img = Image.open(io.BytesIO(image_bytes))
                            
                            # Convert to base64 with proper padding
                            base64_data = base64.b64encode(image_bytes).decode('utf-8')
                            data_uri = f"data:image/png;base64,{base64_data}"
                            
                            png_count += 1
                            print(f"  Photo {photo_id}: PNG fixed ({len(image_bytes)} bytes)")
                            
                        elif image_bytes.startswith(b'\xff\xd8'):
                            # JPEG
                            base64_data = base64.b64encode(image_bytes).decode('utf-8')
                            data_uri = f"data:image/jpeg;base64,{base64_data}"
                            
                            jpeg_count += 1
                            print(f"  Photo {photo_id}: JPEG fixed ({len(image_bytes)} bytes)")
                            
                        else:
                            # Unknown format - treat as JPEG
                            base64_data = base64.b64encode(image_bytes).decode('utf-8')
                            data_uri = f"data:image/jpeg;base64,{base64_data}"
                            
                            print(f"  Photo {photo_id}: Unknown format, treating as JPEG ({len(image_bytes)} bytes)")
                        
                        # Update database
                        cursor.execute(
                            'UPDATE inspection_photos SET image_data = %s WHERE id = %s',
                            (data_uri, photo_id)
                        )
                        
                        fixed_count += 1
                        
                    except Exception as e:
                        print(f"  Photo {photo_id}: ERROR fixing - {e}")
                        continue
                
                elif isinstance(image_data, str) and image_data.startswith('data:image'):
                    # Already in correct format - skip
                    continue
                
                else:
                    print(f"  Photo {photo_id}: Unexpected format - {type(image_data)}")
                    
            except Exception as e:
                print(f"  Photo {photo_id}: ERROR - {e}")
                continue
        
        # Commit changes
        conn.commit()
        
        print(f"\n=== FIX SUMMARY ===")
        print(f"Total photos fixed: {fixed_count}")
        print(f"PNG images (transparency preserved): {png_count}")
        print(f"JPEG images: {jpeg_count}")
        
        cursor.close()
        conn.close()
        
        print(f"\n=== NEXT STEPS ===")
        print("1. Deploy the updated code")
        print("2. Test croqui overlay functionality")
        print("3. Verify all photos display correctly")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_photo_format()
