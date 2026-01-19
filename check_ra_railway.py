#!/usr/bin/env python3
"""
Script para verificar dados do RA no Railway PostgreSQL
Execute este script no Railway ou configure as variáveis de ambiente localmente
"""
import os
import sys
import json

# Verificar se as variáveis de ambiente estão configuradas
required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print("❌ Variáveis de ambiente em falta:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\n💡 Para executar localmente, configure:")
    print("   export DB_HOST=your_railway_host")
    print("   export DB_NAME=railway")
    print("   export DB_USER=postgres")
    print("   export DB_PASSWORD=your_password")
    print("\n💡 Ou execute este script diretamente no Railway")
    sys.exit(1)

import psycopg2

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cursor = conn.cursor()
    
    # Buscar os 5 RAs mais recentes
    cursor.execute("""
        SELECT rental_agreement_number, license_plate, 
               SUBSTRING(extracted_data::text, 1, 100) as preview,
               created_at
        FROM rental_agreements 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    rows = cursor.fetchall()
    
    print(f"\n📋 Found {len(rows)} recent RAs:\n")
    for i, row in enumerate(rows, 1):
        print(f"{i}. RA: {row[0]} | Plate: {row[1]} | Created: {row[3]}")
    
    # Buscar o RA mais recente com detalhes completos
    print("\n" + "="*80)
    print("Checking most recent RA (06716-09)...")
    print("="*80 + "\n")
    
    cursor.execute("""
        SELECT rental_agreement_number, license_plate, extracted_data 
        FROM rental_agreements 
        WHERE rental_agreement_number LIKE %s
        ORDER BY created_at DESC 
        LIMIT 1
    """, ('06716%',))
    
    row = cursor.fetchone()
    if row:
        print(f"✅ RA Found: {row[0]}")
        print(f"📋 License Plate: {row[1]}")
        
        if row[2]:
            try:
                data = json.loads(row[2])
                print(f"\n📋 Extracted Data Keys: {list(data.keys())}")
                print(f"\n📋 Full Extracted Data:")
                for key, value in data.items():
                    print(f"   {key}: {value}")
                
                print(f"\n🔍 Checking specific fields for email:")
                print(f"   clientName: {data.get('clientName', '❌ NOT FOUND')}")
                print(f"   country: {data.get('country', '❌ NOT FOUND')}")
                print(f"   pickupLocation: {data.get('pickupLocation', '❌ NOT FOUND')}")
                print(f"   returnLocation: {data.get('returnLocation', '❌ NOT FOUND')}")
                print(f"   clientEmail: {data.get('clientEmail', '❌ NOT FOUND')}")
            except Exception as e:
                print(f"❌ Error parsing extracted_data: {e}")
                print(f"Raw data preview: {str(row[2])[:200]}...")
        else:
            print("⚠️  No extracted_data found")
    else:
        print("❌ RA 06716-09 not found")
    
    conn.close()
    print("\n✅ Done!")

except Exception as e:
    print(f"❌ Database connection error: {e}")
    sys.exit(1)
