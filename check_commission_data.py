#!/usr/bin/env python3
"""
Script para verificar os dados das comissões importadas
"""
import os
import psycopg2
from urllib.parse import urlparse

def check_commissions():
    """Verifica os dados das comissões na base de dados"""
    
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
        
        # Verificar algumas comissões de março
        print("\n📋 Verificando comissões de março 2026:")
        
        cursor.execute("""
            SELECT 
                cb.id, cb.voucher_number, cb.pickup_date, cb.dropoff_date,
                cb.base_price, cb.commission_amount, cb.commission_rate,
                c.name as commissioner_name
            FROM commission_bookings cb
            LEFT JOIN commissioners c ON cb.commissioner_id = c.id
            WHERE EXTRACT(MONTH FROM cb.pickup_date) = 3
            AND EXTRACT(YEAR FROM cb.pickup_date) = 2026
            ORDER BY cb.pickup_date
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        
        print("\n" + "=" * 100)
        print(f"{'ID':<5} {'Voucher':<20} {'Data':<12} {'Base Price':<12} {'Rate':<8} {'Commission':<12} {'Commissioner':<25}")
        print("=" * 100)
        
        for row in rows:
            booking_id = row[0]
            voucher = row[1] or '-'
            pickup_date = row[2].strftime('%d/%m/%Y') if row[2] else '-'
            base_price = float(row[4]) if row[4] else 0
            commission_amount = float(row[5]) if row[5] else 0
            commission_rate = float(row[6]) if row[6] else 0
            commissioner_name = row[7] if row[7] else 'Unknown'
            
            # Verificar se a comissão está correta
            expected_commission = (base_price / 1.23) * (commission_rate / 100)
            is_correct = abs(commission_amount - expected_commission) < 0.01
            
            print(f"{booking_id:<5} {voucher:<20} {pickup_date:<12} {base_price:<12.2f} {commission_rate:<8.1f} {commission_amount:<12.2f} {commissioner_name:<25} {'✅' if is_correct else '❌'}")
        
        print("=" * 100)
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    check_commissions()
