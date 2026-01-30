import psycopg2
import os

# Credenciais do Railway
DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

try:
    print("🔌 Conectando à base de dados do Railway...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 1. Verificar se a tabela existe
    print("\n1️⃣ Verificando se a tabela parking_qr_codes existe...")
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'parking_qr_codes'
        )
    """)
    table_exists = cursor.fetchone()[0]
    print(f"   Tabela existe: {table_exists}")
    
    if not table_exists:
        print("❌ ERRO: Tabela parking_qr_codes não existe!")
        exit(1)
    
    # 2. Verificar colunas da tabela
    print("\n2️⃣ Verificando colunas da tabela parking_qr_codes...")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'parking_qr_codes'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f"   Colunas encontradas ({len(columns)}):")
    has_pdf_data = False
    for col_name, col_type in columns:
        print(f"   - {col_name} ({col_type})")
        if col_name == 'pdf_data':
            has_pdf_data = True
    
    if not has_pdf_data:
        print("\n❌ COLUNA pdf_data NÃO EXISTE!")
        print("   Vou adicionar agora...")
        cursor.execute("""
            ALTER TABLE parking_qr_codes 
            ADD COLUMN pdf_data TEXT
        """)
        conn.commit()
        print("   ✅ Coluna pdf_data adicionada!")
    else:
        print("\n✅ Coluna pdf_data JÁ EXISTE!")
    
    # 3. Verificar dados para RA 06761
    print("\n3️⃣ Verificando dados para RA 06761...")
    cursor.execute("""
        SELECT ra_number, parking_number, extracted_reference, extracted_date, extracted_time,
               CASE WHEN pdf_data IS NULL THEN 'NULL' ELSE 'EXISTS' END as pdf_status
        FROM parking_qr_codes
        WHERE ra_number = '06761'
    """)
    
    rows = cursor.fetchall()
    if rows:
        print(f"   Encontrados {len(rows)} registos:")
        for row in rows:
            print(f"   - RA: {row[0]}, Parque: {row[1]}, Ref: {row[2]}, Data: {row[3]}, Hora: {row[4]}, PDF: {row[5]}")
    else:
        print("   ❌ Nenhum registo encontrado para RA 06761")
    
    # 4. Verificar colunas da tabela rental_agreements
    print("\n4️⃣ Verificando colunas da tabela rental_agreements...")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'rental_agreements'
        ORDER BY ordinal_position
    """)
    
    ra_columns = cursor.fetchall()
    print(f"   Colunas encontradas ({len(ra_columns)}):")
    for col_name, col_type in ra_columns[:15]:  # Mostrar apenas as primeiras 15
        print(f"   - {col_name} ({col_type})")
    
    # 5. Verificar todos os RAs com QR codes
    print("\n5️⃣ Verificando todos os RAs com QR codes...")
    cursor.execute("""
        SELECT ra_number, COUNT(*) as total,
               SUM(CASE WHEN pdf_data IS NOT NULL THEN 1 ELSE 0 END) as with_pdf
        FROM parking_qr_codes
        GROUP BY ra_number
        ORDER BY ra_number
    """)
    
    all_ras = cursor.fetchall()
    if all_ras:
        print(f"   Total de RAs com QR codes: {len(all_ras)}")
        for ra, total, with_pdf in all_ras:
            print(f"   - RA {ra}: {total} QR codes, {with_pdf} com PDF")
    else:
        print("   ❌ Nenhum QR code encontrado na base de dados")
    
    cursor.close()
    conn.close()
    print("\n🎉 Verificação concluída!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
