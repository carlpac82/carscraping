#!/usr/bin/env python3
"""
Script para comparar as comissões de março 2026 com os valores do Excel
"""
import os
import psycopg2
from urllib.parse import urlparse

def compare_commissions():
    """Compara as comissões na base de dados com os valores esperados"""
    
    # Dados esperados do Excel
    expected_data = {
        'CERRO MAR GARDEM': [
            {'date': '2026-03-24', 'days': 5, 'commission': 170}
        ],
        'CLUBE MARIA LUISA': [
            {'date': '2026-03-05', 'days': 6, 'commission': 160},
            {'date': '2026-03-13', 'days': 2, 'commission': 85},
            {'date': '2026-03-13', 'days': 2, 'commission': 85}
        ],
        'EPIC SANA': [
            {'date': '2026-03-07', 'days': 3, 'commission': 70},
            {'date': '2026-03-07', 'days': 3, 'commission': 50},
            {'date': '2026-03-13', 'days': 3, 'commission': 70}
        ],
        'EXPOSE I': [
            {'date': '2026-03-12', 'days': 5, 'commission': 50, 'voucher': '8258'},
            {'date': '2026-03-16', 'days': 7, 'commission': 100, 'voucher': '8262'},
            {'date': '2026-03-17', 'days': 3, 'commission': 50, 'voucher': '8263'},
            {'date': '2026-03-24', 'days': 3, 'commission': 50, 'voucher': '8264'},
            {'date': '2026-03-27', 'days': 2, 'commission': 70, 'voucher': '8265'}
        ],
        'FALESIA HOTEL': [
            {'date': '2026-03-18', 'days': 5, 'commission': 80},
            {'date': '2026-03-23', 'days': 5, 'commission': 80},
            {'date': '2026-03-27', 'days': 3, 'commission': 60},
            {'date': '2026-03-30', 'days': 3, 'commission': 75},
            {'date': '2026-03-31', 'days': 3, 'commission': 75}
        ],
        'HOLIDAY IN (REAL BELA VISTA)': [
            {'date': '2026-03-21', 'days': 3, 'commission': 50}
        ],
        'INATEL': [
            {'date': '2026-03-09', 'days': 3, 'commission': 50}
        ],
        'MASANA': [
            {'date': '2026-03-14', 'days': 3, 'commission': 50}
        ],
        'OCEANUS': [
            {'date': '2026-03-26', 'days': 3, 'commission': 100}
        ],
        'OURA ATLANTICO': [
            {'date': '2026-03-04', 'days': 5, 'commission': 90}
        ],
        'OURA VIEW BEACH CLUB': [
            {'date': '2026-03-02', 'days': 4, 'commission': 65},
            {'date': '2026-03-03', 'days': 2, 'commission': 45}
        ],
        'PALADIM': [
            {'date': '2026-03-26', 'days': 4, 'commission': 120}
        ],
        'PATEO VILLAGE': [
            {'date': '2026-03-03', 'days': 3, 'commission': 50, 'voucher': '6319'}
        ],
        'PATIO SUITE HOTEL': [
            {'date': '2026-03-07', 'days': 3, 'commission': 70},
            {'date': '2026-03-15', 'days': 2, 'commission': 60},
            {'date': '2026-03-15', 'days': 4, 'commission': 70},
            {'date': '2026-03-18', 'days': 1, 'commission': 35}
        ],
        'PTO': [
            {'date': '2026-03-09', 'days': 5, 'commission': 80, 'voucher': '8779'},
            {'date': '2026-03-12', 'days': 4, 'commission': 65, 'voucher': '8780'},
            {'date': '2026-03-21', 'days': 2, 'commission': 45, 'voucher': '9483'},
            {'date': '2026-03-21', 'days': 3, 'commission': 50, 'voucher': '9482'},
            {'date': '2026-03-22', 'days': 2, 'commission': 45},
            {'date': '2026-03-27', 'days': 3, 'commission': 50, 'voucher': '9484'}
        ],
        'ROCAMAR': [
            {'date': '2026-03-10', 'days': 1, 'commission': 40},
            {'date': '2026-03-20', 'days': 3, 'commission': 50},
            {'date': '2026-03-24', 'days': 4, 'commission': 90},
            {'date': '2026-03-25', 'days': 3, 'commission': 75}
        ],
        'SOL E MAR': [
            {'date': '2026-03-24', 'days': 3, 'commission': 130}
        ],
        'ZEBRA SAFARIS II': [
            {'date': '2026-03-09', 'days': 4, 'commission': 65, 'voucher': '9558'},
            {'date': '2026-03-16', 'days': 3, 'commission': 50, 'voucher': '9559'}
        ]
    }
    
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
        
        # Buscar todas as comissões de março 2026
        cursor.execute("""
            SELECT 
                cb.id, cb.voucher_number, cb.pickup_date, cb.dropoff_date,
                cb.commission_amount, cb.base_price, cb.commission_rate,
                c.name as commissioner_name
            FROM commission_bookings cb
            LEFT JOIN commissioners c ON cb.commissioner_id = c.id
            WHERE EXTRACT(MONTH FROM cb.pickup_date) = 3
            AND EXTRACT(YEAR FROM cb.pickup_date) = 2026
            ORDER BY c.name, cb.pickup_date
        """)
        
        db_rows = cursor.fetchall()
        
        print("\n" + "=" * 120)
        print("COMPARAÇÃO DE COMISSÕES MARÇO 2026")
        print("=" * 120)
        
        all_correct = True
        total_mismatch = 0
        
        for commissioner_name, expected_bookings in expected_data.items():
            print(f"\n🏨 {commissioner_name}")
            print("-" * 60)
            
            # Buscar reservas deste comissionista na BD
            db_bookings = [
                {
                    'id': row[0],
                    'voucher': row[1],
                    'pickup_date': row[2].strftime('%Y-%m-%d'),
                    'commission': float(row[4]),
                    'base_price': float(row[5])
                }
                for row in db_rows if row[7] == commissioner_name
            ]
            
            # Comparar cada reserva esperada
            for i, expected in enumerate(expected_bookings):
                expected_date = expected['date']
                expected_commission = expected['commission']
                expected_voucher = expected.get('voucher', None)
                
                # Procurar reserva correspondente na BD
                found = False
                for db_booking in db_bookings:
                    if (db_booking['pickup_date'] == expected_date and 
                        abs(db_booking['commission'] - expected_commission) < 0.01):
                        
                        # Verificar voucher se esperado
                        voucher_match = True
                        if expected_voucher:
                            voucher_match = db_booking['voucher'] == expected_voucher
                        
                        status = "✅" if voucher_match else "⚠️"
                        voucher_info = f" (voucher: {db_booking['voucher']})" if db_booking['voucher'] else ""
                        
                        print(f"  {status} {expected_date} - €{expected_commission:>6} -> BD: €{db_booking['commission']:>6.2f}{voucher_info}")
                        found = True
                        break
                
                if not found:
                    print(f"  ❌ {expected_date} - €{expected_commission:>6} -> NÃO ENCONTRADO NA BD")
                    all_correct = False
                    total_mismatch += 1
        
        print("\n" + "=" * 120)
        if all_correct:
            print("✅ TODAS AS COMISSÕES CORRESPONDEM!")
        else:
            print(f"❌ {total_mismatch} comissões não correspondem")
        print("=" * 120)
        
        cursor.close()
        conn.close()
        return all_correct
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    compare_commissions()
