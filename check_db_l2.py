import os
import psycopg2
from urllib.parse import urlparse
import json

# Get database URL from environment
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    print("❌ DATABASE_URL não encontrada nas variáveis de ambiente")
    print("Execute: export DATABASE_URL='sua_url_aqui'")
    exit(1)

# Parse database URL
url = urlparse(database_url)

# Connect to database
conn = psycopg2.connect(
    host=url.hostname,
    port=url.port,
    user=url.username,
    password=url.password,
    database=url.path[1:]
)

print("✅ Conectado à base de dados\n")

# Query for March 2026 period 27-31
cur = conn.cursor()
cur.execute("""
    SELECT id, location, month, year, day_start, day_end, prices_data, updated_at, updated_by
    FROM current_prices
    WHERE month = 'March' AND year = 2026 AND day_start = 27 AND day_end = 31
""")

results = cur.fetchall()

if not results:
    print("❌ Nenhum período encontrado para Março 2026, dias 27-31")
else:
    print(f"📊 Encontrados {len(results)} registos:\n")
    
    for row in results:
        id_val, location, month, year, day_start, day_end, prices_data, updated_at, updated_by = row
        
        print(f"{'='*80}")
        print(f"ID: {id_val}")
        print(f"Location: {location}")
        print(f"Período: {month} {year}, dias {day_start}-{day_end}")
        print(f"Atualizado: {updated_at} por {updated_by}")
        print(f"\n{'='*80}")
        
        # Parse prices_data
        if prices_data:
            prices = json.loads(prices_data) if isinstance(prices_data, str) else prices_data
            
            # Check if L2 exists
            if 'L2' in prices:
                print("\n🔍 GRUPO L2 ENCONTRADO:")
                l2_prices = prices['L2']
                
                # Show all L2 prices
                for dia, preco in sorted(l2_prices.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
                    print(f"  {dia} dias: {preco}")
                
                # Highlight 2-day price
                if '2' in l2_prices:
                    print(f"\n⭐ Preço de 2 dias: {l2_prices['2']}")
                elif '2_day_fixed' in l2_prices:
                    print(f"\n⭐ Preço de 2 dias (old format): {l2_prices['2_day_fixed']}")
                else:
                    print("\n❌ Preço de 2 dias NÃO ENCONTRADO")
            else:
                print("\n❌ Grupo L2 NÃO ENCONTRADO nos dados")
                print(f"Grupos disponíveis: {list(prices.keys())}")
        else:
            print("\n❌ prices_data está vazio")
        
        print(f"\n{'='*80}\n")

# Also check all March 2026 periods
print("\n\n📋 TODOS OS PERÍODOS DE MARÇO 2026:\n")
cur.execute("""
    SELECT id, location, day_start, day_end, updated_at, updated_by
    FROM current_prices
    WHERE month = 'March' AND year = 2026
    ORDER BY location, day_start
""")

all_periods = cur.fetchall()
for row in all_periods:
    id_val, location, day_start, day_end, updated_at, updated_by = row
    print(f"ID {id_val}: {location} - dias {day_start}-{day_end} (atualizado: {updated_at} por {updated_by})")

cur.close()
conn.close()

print("\n✅ Análise concluída")
