#!/usr/bin/env python3
"""
Script para verificar a interpretação correta dos dados do Excel
"""
import os
import psycopg2
from urllib.parse import urlparse

def check_interpretation():
    """Verifica se os valores do Excel foram interpretados corretamente"""
    
    # Exemplo: CERRO MAR GARDEM - 2026-03-24 - 5 dias - 170
    # Se 170 é base_price, então commission_amount = (170 / 1.23) * 0.15 = 20.73
    
    # Obter DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        database_url = line.split('=', 1)[1].strip()
                        break
        except:
            pass
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    # Parse da URL
    result = urlparse(database_url)
    
    try:
        # Conectar à base de dados
        print(f"🔌 Conectando a {result.hostname}...")
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        print("✅ Conectado à base de dados")
        
        # Verificar CERRO MAR GARDEM
        cursor.execute("""
            SELECT 
                cb.id, cb.voucher_number, cb.pickup_date, cb.dropoff_date,
                cb.base_price, cb.commission_amount, cb.commission_rate,
                c.name as commissioner_name
            FROM commission_bookings cb
            LEFT JOIN commissioners c ON cb.commissioner_id = c.id
            WHERE c.name = 'CERRO MAR GARDEM'
            AND cb.pickup_date = '2026-03-24'
        """)
        
        row = cursor.fetchone()
        
        if row:
            print("\n" + "=" * 80)
            print("CERRO MAR GARDEM - 2026-03-24")
            print("=" * 80)
            print(f"Valor no Excel: 170")
            print(f"Base Price na BD: {row[4]}")
            print(f"Commission Amount na BD: {row[5]}")
            print(f"Commission Rate: {row[6]}%")
            
            # Calcular comissão correta se 170 for base_price
            correct_commission = (170 / 1.23) * 0.15
            print(f"\nSe 170 for BASE_PRICE:")
            print(f"  Comissão correta: €{correct_commission:.2f}")
            print(f"  Comissão na BD: €{row[5]}")
            print(f"  Diferença: €{abs(row[5] - correct_commission):.2f}")
            
            if abs(row[5] - 170) < 0.01:
                print(f"\n❌ ERRO: A BD está a guardar 170 como COMISSÃO em vez de BASE_PRICE!")
                print(f"   Valor correto da comissão deveria ser: €{correct_commission:.2f}")
            else:
                print(f"\n✅ Valores parecem corretos")
        
        print("\n" + "=" * 80)
        print("VERIFICANDO MAIS EXEMPLOS:")
        print("=" * 80)
        
        # Verificar mais exemplos
        cursor.execute("""
            SELECT 
                cb.pickup_date, cb.base_price, cb.commission_amount,
                c.name as commissioner_name
            FROM commission_bookings cb
            LEFT JOIN commissioners c ON cb.commissioner_id = c.id
            WHERE EXTRACT(MONTH FROM cb.pickup_date) = 3
            AND EXTRACT(YEAR FROM cb.pickup_date) = 2026
            ORDER BY cb.pickup_date
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        
        print(f"{'Data':<12} {'Base Price':<12} {'Commission':<12} {'Commissioner':<25}")
        print("-" * 70)
        
        for row in rows:
            date = row[0].strftime('%d/%m/%Y')
            base_price = row[1]
            commission = row[2]
            commissioner = row[3]
            
            # Verificar se commission parece ser base_price
            if commission > 100:  # Comissões altas podem indicar erro
                print(f"{date:<12} {base_price:<12.2f} {commission:<12.2f} {commissioner:<25} ⚠️")
            else:
                print(f"{date:<12} {base_price:<12.2f} {commission:<12.2f} {commissioner:<25}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    check_interpretation()
