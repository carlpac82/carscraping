#!/usr/bin/env python3
"""
Script para corrigir padding base64 de fotos e assinaturas na base de dados PostgreSQL
"""
import os
import psycopg2
from urllib.parse import urlparse

def fix_base64_padding(data_uri):
    """Fix base64 padding in a data URI string"""
    if not data_uri or not isinstance(data_uri, str):
        return data_uri
    
    if not data_uri.startswith('data:image'):
        return data_uri
    
    parts = data_uri.split(',', 1)
    if len(parts) != 2:
        return data_uri
    
    header, encoded = parts
    
    # Remove whitespace
    encoded = encoded.strip().replace('\n', '').replace('\r', '').replace(' ', '')
    
    # Calculate and add padding
    padding_needed = (4 - len(encoded) % 4) % 4
    if padding_needed:
        encoded += '=' * padding_needed
        print(f"  ✅ Added {padding_needed} padding chars (length: {len(encoded)})")
    else:
        print(f"  ℹ️  No padding needed (length: {len(encoded)})")
    
    return f"{header},{encoded}"

def main():
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return
    
    # Parse database URL
    result = urlparse(database_url)
    
    # Connect to PostgreSQL
    print("🔌 Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=result.hostname,
        port=result.port,
        user=result.username,
        password=result.password,
        database=result.path[1:]
    )
    cursor = conn.cursor()
    
    # Fix inspection_photos
    print("\n📸 Fixing inspection_photos...")
    cursor.execute("SELECT id, image_data FROM inspection_photos WHERE image_data LIKE 'data:image%'")
    photos = cursor.fetchall()
    print(f"Found {len(photos)} photos to check")
    
    fixed_photos = 0
    for photo_id, image_data in photos:
        fixed_data = fix_base64_padding(image_data)
        if fixed_data != image_data:
            cursor.execute("UPDATE inspection_photos SET image_data = %s WHERE id = %s", (fixed_data, photo_id))
            fixed_photos += 1
            print(f"  🔧 Fixed photo ID {photo_id}")
    
    print(f"✅ Fixed {fixed_photos} photos")
    
    # Fix vehicle_inspections signatures
    print("\n✍️ Fixing signatures...")
    cursor.execute("SELECT id, signature FROM vehicle_inspections WHERE signature LIKE 'data:image%'")
    signatures = cursor.fetchall()
    print(f"Found {len(signatures)} signatures to check")
    
    fixed_sigs = 0
    for inspection_id, signature in signatures:
        fixed_sig = fix_base64_padding(signature)
        if fixed_sig != signature:
            cursor.execute("UPDATE vehicle_inspections SET signature = %s WHERE id = %s", (fixed_sig, inspection_id))
            fixed_sigs += 1
            print(f"  🔧 Fixed signature for inspection ID {inspection_id}")
    
    print(f"✅ Fixed {fixed_sigs} signatures")
    
    # Commit changes
    conn.commit()
    print("\n✅ All changes committed to database")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
