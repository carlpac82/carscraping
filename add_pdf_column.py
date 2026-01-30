import psycopg2
import os

# Credenciais do Railway
DATABASE_URL = "postgresql://postgres:EYXxkqjVPUwpMOTDXmhYDaZbzKLVDIqp@autorack.proxy.rlwy.net:47689/railway"

try:
    print("🔌 Conectando à base de dados do Railway...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("🔧 Adicionando coluna pdf_data à tabela parking_qr_codes...")
    cursor.execute("""
        ALTER TABLE parking_qr_codes 
        ADD COLUMN IF NOT EXISTS pdf_data TEXT
    """)
    
    conn.commit()
    print("✅ Coluna pdf_data adicionada com sucesso!")
    
    # Verificar se a coluna foi adicionada
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'parking_qr_codes'
    """)
    
    columns = [row[0] for row in cursor.fetchall()]
    print(f"\n📋 Colunas da tabela parking_qr_codes:")
    for col in columns:
        print(f"  - {col}")
    
    if 'pdf_data' in columns:
        print("\n✅ Confirmado: coluna pdf_data existe!")
    else:
        print("\n❌ ERRO: coluna pdf_data não foi adicionada!")
    
    cursor.close()
    conn.close()
    print("\n🎉 Concluído!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
