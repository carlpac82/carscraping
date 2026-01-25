#!/usr/bin/env python3
"""
EMERGENCY FIX: Remove o último caractere de cada base64 para compensar o bug do código antigo
O código antigo está a adicionar 1 caractere extra, então vamos remover 1 caractere de cada foto
"""
import os
import sys

# Add parent directory to path to import database connection
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_photos():
    """Remove 1 character from each base64 to compensate for old code bug"""
    try:
        # Import database connection from main
        from main import _db_connect
        
        conn = _db_connect()
        cursor = conn.cursor()
        
        print("🔧 Starting emergency base64 fix...")
        print("📊 This will remove 1 character from each base64 to compensate for old code")
        
        # Fix inspection_photos
        cursor.execute("SELECT id, image_data, photo_type FROM inspection_photos WHERE image_data LIKE 'data:image%'")
        photos = cursor.fetchall()
        
        print(f"\n📸 Found {len(photos)} photos to fix")
        
        fixed_count = 0
        for photo_id, image_data, photo_type in photos:
            if not image_data or not image_data.startswith('data:image'):
                continue
            
            parts = image_data.split(',', 1)
            if len(parts) != 2:
                continue
            
            header, encoded = parts
            original_len = len(encoded)
            
            # Remove last character to compensate for old code adding 1 extra
            if len(encoded) > 0:
                encoded_fixed = encoded[:-1]  # Remove last char
                fixed_data = f"{header},{encoded_fixed}"
                
                cursor.execute("UPDATE inspection_photos SET image_data = %s WHERE id = %s", (fixed_data, photo_id))
                fixed_count += 1
                print(f"  ✅ Fixed photo ID {photo_id} ({photo_type}): {original_len} -> {len(encoded_fixed)} chars")
        
        # Fix signatures
        cursor.execute("SELECT id, signature FROM vehicle_inspections WHERE signature LIKE 'data:image%'")
        signatures = cursor.fetchall()
        
        print(f"\n✍️ Found {len(signatures)} signatures to fix")
        
        fixed_sigs = 0
        for inspection_id, signature in signatures:
            if not signature or not signature.startswith('data:image'):
                continue
            
            parts = signature.split(',', 1)
            if len(parts) != 2:
                continue
            
            header, encoded = parts
            original_len = len(encoded)
            
            # Remove last character
            if len(encoded) > 0:
                encoded_fixed = encoded[:-1]
                fixed_sig = f"{header},{encoded_fixed}"
                
                cursor.execute("UPDATE vehicle_inspections SET signature = %s WHERE id = %s", (fixed_sig, inspection_id))
                fixed_sigs += 1
                print(f"  ✅ Fixed signature for inspection ID {inspection_id}: {original_len} -> {len(encoded_fixed)} chars")
        
        conn.commit()
        print(f"\n✅ SUCCESS! Fixed {fixed_count} photos and {fixed_sigs} signatures")
        print("🔄 Now test the PDF again - it should work with the old code")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = fix_photos()
    sys.exit(0 if success else 1)
