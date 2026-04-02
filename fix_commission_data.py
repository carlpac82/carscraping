#!/usr/bin/env python3
"""
Script para corrigir os dados das comissões importadas
Transformar os valores de commission_amount em base_price e calcular a comissão correta
"""
import os
import psycopg2
from urllib.parse import urlparse

def fix_commission_data():
    """Corrige os dados das comissões importadas"""
    
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
        
        # Buscar todas as comissões importadas (janeiro, fevereiro, março)
        print("\n📋 Buscando comissões importadas...")
        
        cursor.execute("""
            SELECT 
                cb.id, cb.base_price, cb.commission_amount, cb.commission_rate,
                cb.pickup_date, c.name as commissioner_name
            FROM commission_bookings cb
            LEFT JOIN commissioners c ON cb.commissioner_id = c.id
            WHERE cb.client_name = 'Loyalty Card'
            AND (EXTRACT(MONTH FROM cb.pickup_date) IN (1, 2, 3))
            AND EXTRACT(YEAR FROM cb.pickup_date) = 2026
            ORDER BY cb.pickup_date
        """)
        
        rows = cursor.fetchall()
        
        print(f"\n📊 Encontradas {len(rows)} comissões para corrigir")
        
        fixed_count = 0
        error_count = 0
        
        for row in rows:
            booking_id = row[0]
            current_base_price = float(row[1])
            current_commission = float(row[2])
            commission_rate = float(row[3])
            pickup_date = row[4]
            commissioner_name = row[5]
            
            # O valor atual em commission_amount é na verdade o base_price do Excel
            excel_base_price = current_commission
            
            # Calcular a comissão correta
            correct_commission = (excel_base_price / 1.23) * (commission_rate / 100.0)
            
            # Atualizar os valores
            try:
                cursor.execute("""
                    UPDATE commission_bookings 
                    SET base_price = %s, commission_amount = %s
                    WHERE id = %s
                """, (excel_base_price, correct_commission, booking_id))
                
                print(f"✅ {commissioner_name} - {pickup_date.strftime('%d/%m/%Y')}: "
                      f"Base: €{excel_base_price:.2f} → Comissão: €{correct_commission:.2f}")
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ Erro ao corrigir booking {booking_id}: {e}")
                error_count += 1
        
        # Commit das alterações
        conn.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Correção concluída!")
        print(f"  - Reservas corrigidas: {fixed_count}")
        print(f"  - Erros: {error_count}")
        print("=" * 80)
        
        cursor.close()
        conn.close()
        return error_count == 0
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = fix_commission_data()
    exit(0 if success else 1)
