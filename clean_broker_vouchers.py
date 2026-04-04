import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Count vouchers to be cleaned
    cur.execute("""
        SELECT COUNT(*)
        FROM broker_bookings
        WHERE voucher_number LIKE 'AP-%'
    """)
    
    total_before = cur.fetchone()[0]
    print(f"\n📊 Total de vouchers AP-XX a limpar: {total_before}")
    
    # Clean AP-XX vouchers - set to NULL
    cur.execute("""
        UPDATE broker_bookings
        SET voucher_number = NULL
        WHERE voucher_number LIKE 'AP-%'
    """)
    
    updated = cur.rowcount
    conn.commit()
    
    print(f"✅ {updated} vouchers AP-XX foram limpos (definidos como NULL)")
    
    # Verify cleanup
    cur.execute("""
        SELECT COUNT(*)
        FROM broker_bookings
        WHERE voucher_number LIKE 'AP-%'
    """)
    
    total_after = cur.fetchone()[0]
    print(f"📊 Total de vouchers AP-XX após limpeza: {total_after}")
    
    if total_after == 0:
        print("\n✅ Limpeza concluída com sucesso! Todos os vouchers AP-XX foram removidos.")
    else:
        print(f"\n⚠️ Ainda existem {total_after} vouchers AP-XX na base de dados.")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
    if 'conn' in locals():
        conn.rollback()
