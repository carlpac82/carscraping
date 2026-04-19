#!/usr/bin/env python3
"""
Check current state of photos in database
"""

import os
import psycopg2
from urllib.parse import urlparse

def check_photos():
    try:
        # Connect to database
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("ERROR: DATABASE_URL not found")
            return
        
        print("Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Count photos in inspection_photos  
        cursor.execute('SELECT COUNT(*) FROM inspection_photos WHERE image_data IS NOT NULL')
        inspection_count = cursor.fetchone()[0]
        
        # Check sample photo formats
        cursor.execute('SELECT image_data FROM inspection_photos WHERE image_data IS NOT NULL LIMIT 5')
        samples = cursor.fetchall()
        
        print(f"\n=== PHOTO STATUS ===")
        print(f"Photos in inspection_photos: {inspection_count}")
        print(f"\nSample photo data types:")
        
        png_count = 0
        jpeg_count = 0
        other_count = 0
        
        for i, (data,) in enumerate(samples):
            if data:
                if isinstance(data, bytes):
                    if data.startswith(b'\\x'):
                        # Convert hex to bytes and check format
                        try:
                            import binascii
                            actual_data = binascii.unhexlify(data[2:])
                            if actual_data.startswith(b'\\x89PNG'):
                                png_count += 1
                                print(f"  Sample {i+1}: PNG (BYTEA hex)")
                            elif actual_data.startswith(b'\\xff\\xd8'):
                                jpeg_count += 1
                                print(f"  Sample {i+1}: JPEG (BYTEA hex)")
                            else:
                                other_count += 1
                                print(f"  Sample {i+1}: Other format (BYTEA hex)")
                        except:
                            print(f"  Sample {i+1}: BYTEA hex (cannot decode)")
                    else:
                        print(f"  Sample {i+1}: Raw bytes")
                elif isinstance(data, str):
                    if data.startswith('data:image'):
                        if 'png' in data:
                            png_count += 1
                            print(f"  Sample {i+1}: PNG (Base64 data URI)")
                        elif 'jpeg' in data or 'jpg' in data:
                            jpeg_count += 1
                            print(f"  Sample {i+1}: JPEG (Base64 data URI)")
                        else:
                            other_count += 1
                            print(f"  Sample {i+1}: Other format (Base64 data URI)")
                    else:
                        # Try to decode base64 to check format
                        try:
                            import base64
                            decoded = base64.b64decode(data)
                            if decoded.startswith(b'\x89PNG'):
                                png_count += 1
                                print(f"  Sample {i+1}: PNG (Base64 string)")
                            elif decoded.startswith(b'\xff\xd8'):
                                jpeg_count += 1
                                print(f"  Sample {i+1}: JPEG (Base64 string)")
                            else:
                                other_count += 1
                                print(f"  Sample {i+1}: Other format (Base64 string)")
                        except:
                            print(f"  Sample {i+1}: Base64 string (cannot decode)")
                else:
                    print(f"  Sample {i+1}: {type(data)}")
        
        print(f"\n=== FORMAT SUMMARY ===")
        print(f"PNG samples: {png_count}")
        print(f"JPEG samples: {jpeg_count}")
        print(f"Other samples: {other_count}")
        
                
        cursor.close()
        conn.close()
        
        print(f"\n=== RECOMMENDATIONS ===")
        if png_count > 0:
            print("PNG images found - transparency should be preserved")
        if jpeg_count > 0:
            print("JPEG images found - normal compression")
        if other_count > 0:
            print("Other formats found - may need special handling")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_photos()
