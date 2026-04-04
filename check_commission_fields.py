import psycopg2

conn = psycopg2.connect('postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway')
cur = conn.cursor()

print('=== VERIFICAR CAMPOS DE COMISSIONISTAS ===')
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(base_price) as com_base_price,
        COUNT(price) as com_price,
        COUNT(total_amount) as com_total_amount,
        SUM(CASE WHEN base_price > 0 THEN 1 ELSE 0 END) as base_price_positivo,
        SUM(CASE WHEN price > 0 THEN 1 ELSE 0 END) as price_positivo,
        SUM(CASE WHEN total_amount > 0 THEN 1 ELSE 0 END) as total_amount_positivo
    FROM commission_bookings
    WHERE EXTRACT(YEAR FROM pickup_date) = 2025
""")

result = cur.fetchone()
print(f'Total registos 2025: {result[0]}')
print(f'Com base_price: {result[1]} (positivos: {result[4]})')
print(f'Com price: {result[2]} (positivos: {result[5]})')
print(f'Com total_amount: {result[3]} (positivos: {result[6]})')

print('\n=== EXEMPLO DE 3 REGISTOS ===')
cur.execute("""
    SELECT base_price, price, total_amount, pickup_date
    FROM commission_bookings
    WHERE EXTRACT(YEAR FROM pickup_date) = 2025
    LIMIT 3
""")

for row in cur.fetchall():
    print(f'base_price: {row[0]}, price: {row[1]}, total_amount: {row[2]}, data: {row[3]}')

conn.close()
