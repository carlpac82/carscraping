import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("=== Atualizando base_price em commission_bookings para 2025 ===\n")

# Atualizar base_price com o valor de price para todos os registos de 2025
cur.execute("""
    UPDATE commission_bookings
    SET base_price = price
    WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    AND base_price IS NULL
    AND price IS NOT NULL
""")

rows_updated = cur.rowcount
conn.commit()

print(f"✅ {rows_updated} registos atualizados com sucesso!")

# Verificar resultado
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(base_price) as base_price_filled,
        COUNT(price) as price_filled
    FROM commission_bookings
    WHERE EXTRACT(YEAR FROM pickup_date) = 2025
""")

row = cur.fetchone()
print(f"\nVerificação:")
print(f"Total de registos 2025: {row[0]}")
print(f"Com base_price: {row[1]}")
print(f"Com price: {row[2]}")

# Mostrar exemplos
print("\n=== Exemplos após atualização (primeiros 3) ===")
cur.execute("""
    SELECT 
        id, voucher_number, pickup_date, 
        base_price, price
    FROM commission_bookings
    WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    ORDER BY pickup_date
    LIMIT 3
""")

for row in cur.fetchall():
    print(f"\nID: {row[0]}, Voucher: {row[1]}, Data: {row[2]}")
    print(f"  base_price: {row[3]}")
    print(f"  price: {row[4]}")

cur.close()
conn.close()
