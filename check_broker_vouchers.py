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
    
    # Check for AP-XX pattern vouchers
    cur.execute("""
        SELECT id, broker_name, voucher_number, pickup_date, total_price
        FROM broker_bookings
        WHERE voucher_number LIKE 'AP-%'
        ORDER BY pickup_date DESC
        LIMIT 50
    """)
    
    rows = cur.fetchall()
    
    if rows:
        print(f"\n🔍 Encontrados {len(rows)} vouchers com padrão AP-XX:\n")
        for row in rows:
            print(f"ID: {row[0]}, Broker: {row[1]}, Voucher: {row[2]}, Data: {row[3]}, Valor: {row[4]}")
    else:
        print("\n✅ Nenhum voucher com padrão AP-XX encontrado")
    
    # Count total AP-XX vouchers
    cur.execute("""
        SELECT COUNT(*)
        FROM broker_bookings
        WHERE voucher_number LIKE 'AP-%'
    """)
    
    total = cur.fetchone()[0]
    print(f"\n📊 Total de vouchers AP-XX na base de dados: {total}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
