#!/usr/bin/env python3
import os
import psycopg2
import json

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
    SELECT rental_agreement_number, extracted_data
    FROM rental_agreements
    WHERE rental_agreement_number LIKE '06691%'
    ORDER BY created_at DESC
    LIMIT 1
""")

row = cursor.fetchone()

if row:
    ra_number = row[0]
    extracted_data = row[1]
    
    print(f"\n{'='*80}")
    print(f"RA: {ra_number}")
    print(f"{'='*80}\n")
    
    if extracted_data:
        data = json.loads(extracted_data) if isinstance(extracted_data, str) else extracted_data
        
        print("📋 CAMPOS DISPONÍVEIS:")
        print(f"   {list(data.keys())}\n")
        
        print("🌍 CAMPOS DE PAÍS:")
        country_fields = ['country', 'pais', 'Country', 'COUNTRY', 'clientCountry', 'client_country']
        for field in country_fields:
            value = data.get(field)
            if value:
                print(f"   ✅ {field}: '{value}'")
            else:
                print(f"   ❌ {field}: (não existe)")
        
        print(f"\n📄 EXTRACTED_DATA COMPLETO:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("⚠️ Sem extracted_data")
else:
    print("❌ RA não encontrado")

conn.close()
