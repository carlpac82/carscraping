import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Buscar configurações de preços para Grupo B
cur.execute("SELECT key, value FROM app_settings WHERE key LIKE 'commissioner_season_b%' OR key LIKE 'commissioner_insurance_b%' ORDER BY key")
settings = cur.fetchall()

print("=" * 80)
print("CONFIGURAÇÕES DE PREÇOS (Grupo B):")
print("=" * 80)
for key, value in settings:
    print(f"{key}: {value}")

print("\n" + "=" * 80)

cur.close()
conn.close()
