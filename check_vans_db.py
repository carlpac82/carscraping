import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT * FROM vans_pricing ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    
    if row:
        print("=" * 60)
        print("VANS PRICING NA BASE DE DADOS:")
        print("=" * 60)
        print(f"ID: {row[0]}")
        print(f"C3 - 1 dia: {row[1]}")
        print(f"C3 - 2 dias: {row[2]}")
        print(f"C3 - 3 dias: {row[3]}")
        print(f"C4 - 1 dia: {row[4]}")
        print(f"C4 - 2 dias: {row[5]}")
        print(f"C4 - 3 dias: {row[6]}")
        print(f"C5 - 1 dia: {row[7]}")
        print(f"C5 - 2 dias: {row[8]}")
        print(f"C5 - 3 dias: {row[9]}")
        print("=" * 60)
        print("\nVALORES ESPERADOS (TOTAIS):")
        print("C3: 112, 144, 180")
        print("C4: 152, 170, 210")
        print("C5: 175, 190, 240")
        print("=" * 60)
    else:
        print("❌ Nenhum registo na tabela vans_pricing!")
    
    conn.close()
else:
    print("❌ DATABASE_URL não definida!")
