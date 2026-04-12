#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL não encontrado no ambiente")
    sys.exit(1)

print(f"DATABASE_URL: {DATABASE_URL}")

# Usar a mesma lógica do database.py
if DATABASE_URL:
    import psycopg2
    from urllib.parse import urlparse
    
    # Parse the database URL
    result = urlparse(DATABASE_URL)
    
    print(f"Parse result:")
    print(f"  scheme: {result.scheme}")
    print(f"  username: {result.username}")
    print(f"  password: {result.password}")
    print(f"  hostname: {result.hostname}")
    print(f"  port: {result.port}")
    print(f"  path: {result.path}")
    print(f"  database: {result.path[1:] if result.path else ''}")
    
    try:
        # Conectar à base de dados
        conn = psycopg2.connect(
            database=result.path[1:] if result.path else '',
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        
        cur = conn.cursor()
        
        # Buscar valores atuais da reserva 6433
        cur.execute("""
            SELECT base_price, premium_insurance, road_tax, extras_total, price, total_amount
            FROM commission_bookings
            WHERE id = 6433
        """)
        
        row = cur.fetchone()
        if row:
            base_price = float(row[0]) if row[0] is not None else 0.0
            premium_insurance = float(row[1]) if row[1] is not None else 0.0
            road_tax = float(row[2]) if row[2] is not None else 0.0
            extras_total = float(row[3]) if row[3] is not None else 0.0
            
            # Calcular o valor correto
            total_calculado = base_price + premium_insurance + road_tax + extras_total
            
            print(f"\nRESERVA OCA-001/26 (ID 6433) - CORREÇÃO DE VALORES")
            print("=" * 60)
            print(f"Valores atuais na BD:")
            print(f"  base_price: {base_price}")
            print(f"  premium_insurance: {premium_insurance}")
            print(f"  road_tax: {road_tax}")
            print(f"  extras_total: {extras_total}")
            print(f"  price: {row[4]}")
            print(f"  total_amount: {row[5]}")
            print()
            print(f"Cálculo correto:")
            print(f"  {base_price} + {premium_insurance} + {road_tax} + {extras_total} = {total_calculado}")
            print()
            
            # Atualizar os valores
            cur.execute("""
                UPDATE commission_bookings
                SET price = %s, total_amount = %s
                WHERE id = 6433
            """, (total_calculado, total_calculado))
            
            conn.commit()
            
            print(f"VALORES ATUALIZADOS:")
            print(f"  price: {total_calculado}")
            print(f"  total_amount: {total_calculado}")
            print()
            print(f">>> RESERVA CORRIGIDA COM SUCESSO! <<<")
            
        else:
            print("Reserva 6433 não encontrada!")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao conectar ou executar operação: {e}")
        import traceback
        traceback.print_exc()
else:
    print("DATABASE_URL não configurado")
