#!/usr/bin/env python3
"""
APENAS VERIFICAR - NÃO ALTERA NADA!
Verifica quais fotos têm problemas de padding
"""
import psycopg2
import os
import base64
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv('DATABASE_URL')

def check_base64(data):
    """Verifica se base64 é válido"""
    if not data:
        return "EMPTY"
    
    # Check if it's hex format
    if isinstance(data, str) and data.startswith('\\x'):
        return "HEX_FORMAT_OK"
    
    # Check if it's base64
    if isinstance(data, str):
        # Remove data URI prefix if present
        if 'data:image' in data:
            parts = data.split(',', 1)
            if len(parts) == 2:
                b64_data = parts[1]
            else:
                b64_data = data
        else:
            b64_data = data
        
        # Try to decode
        try:
            base64.b64decode(b64_data)
            return "BASE64_OK"
        except Exception as e:
            return f"ERROR: {str(e)[:60]}"
    
    return "UNKNOWN_FORMAT"

def main():
    print("🔍 VERIFICANDO dados (SEM ALTERAR NADA)...\n")
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Verificar APENAS croquis primeiro
    cursor.execute("""
        SELECT ip.id, ip.photo_type, vi.inspection_number, LENGTH(ip.image_data::text) as data_len
        FROM inspection_photos ip
        JOIN vehicle_inspections vi ON ip.inspection_id = vi.id
        WHERE ip.photo_type = 'damage_croqui' 
        AND ip.image_data IS NOT NULL
        ORDER BY ip.id DESC
        LIMIT 20
    """)
    
    croquis = cursor.fetchall()
    print(f"📊 CROQUIS (últimos 20):")
    print("="*80)
    
    croqui_ok = 0
    croqui_error = 0
    
    for photo_id, photo_type, inspection_num, data_len in croquis:
        cursor.execute("SELECT image_data FROM inspection_photos WHERE id = %s", (photo_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            status = check_base64(result[0])
            
            if "OK" in status:
                print(f"✅ ID {photo_id} | {inspection_num} | {status}")
                croqui_ok += 1
            else:
                print(f"❌ ID {photo_id} | {inspection_num} | {status}")
                croqui_error += 1
    
    print(f"\n📊 RESUMO CROQUIS: ✅ {croqui_ok} OK | ❌ {croqui_error} COM ERRO")
    
    # Verificar OUTRAS fotos
    print(f"\n{'='*80}")
    print(f"📊 OUTRAS FOTOS (amostra de 50):")
    print("="*80)
    
    cursor.execute("""
        SELECT ip.id, ip.photo_type, vi.inspection_number, LENGTH(ip.image_data::text) as data_len
        FROM inspection_photos ip
        JOIN vehicle_inspections vi ON ip.inspection_id = vi.id
        WHERE ip.photo_type != 'damage_croqui' 
        AND ip.image_data IS NOT NULL
        ORDER BY ip.id DESC
        LIMIT 50
    """)
    
    other_photos = cursor.fetchall()
    
    other_ok = 0
    other_error = 0
    error_by_type = {}
    
    for photo_id, photo_type, inspection_num, data_len in other_photos:
        cursor.execute("SELECT image_data FROM inspection_photos WHERE id = %s", (photo_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            status = check_base64(result[0])
            
            if "OK" in status:
                other_ok += 1
            else:
                print(f"❌ ID {photo_id} | {inspection_num} | {photo_type} | {status}")
                other_error += 1
                
                if photo_type not in error_by_type:
                    error_by_type[photo_type] = 0
                error_by_type[photo_type] += 1
    
    print(f"\n📊 RESUMO OUTRAS FOTOS: ✅ {other_ok} OK | ❌ {other_error} COM ERRO")
    
    if error_by_type:
        print(f"\n📊 ERROS POR TIPO:")
        for ptype, count in sorted(error_by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {ptype}: {count} erros")
    
    cursor.close()
    conn.close()
    
    print(f"\n{'='*80}")
    print(f"🔍 VERIFICAÇÃO COMPLETA - NENHUM DADO FOI ALTERADO")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
