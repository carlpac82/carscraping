import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Verificar estrutura e dados de commission_bookings
print("=== Verificando campos de preço em commission_bookings ===\n")

# Verificar se base_price existe e está preenchido
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(base_price) as base_price_filled,
        COUNT(price) as price_filled,
        COUNT(total_amount) as total_amount_filled
    FROM commission_bookings
    WHERE EXTRACT(YEAR FROM pickup_date) = 2025
""")

row = cur.fetchone()
print(f"Total de registos 2025: {row[0]}")
print(f"Com base_price: {row[1]}")
print(f"Com price: {row[2]}")
print(f"Com total_amount: {row[3]}")

# Mostrar exemplos de valores
print("\n=== Exemplos de valores (primeiros 5 registos) ===")
cur.execute("""
    SELECT 
        id, voucher_number, pickup_date, 
        base_price, price, total_amount,
        premium_insurance, road_tax, extras_total
    FROM commission_bookings
    WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    ORDER BY pickup_date
    LIMIT 5
""")

for row in cur.fetchall():
    print(f"\nID: {row[0]}, Voucher: {row[1]}, Data: {row[2]}")
    print(f"  base_price: {row[3]}")
    print(f"  price: {row[4]}")
    print(f"  total_amount: {row[5]}")
    print(f"  premium_insurance: {row[6]}")
    print(f"  road_tax: {row[7]}")
    print(f"  extras_total: {row[8]}")

cur.close()
conn.close()
