#!/usr/bin/env python3
"""
Script para corrigir dropoff_date nos registos de 2025
Lê os dias CORRETOS dos ficheiros Excel em cm-25/
"""
import os
import pandas as pd
import psycopg2
from urllib.parse import urlparse
from datetime import datetime, timedelta

def fix_2025_from_excel():
    """Atualiza dropoff_date lendo dias dos ficheiros Excel de 2025"""
    
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
        
        # Mapeamento de nomes de hotéis para comissionistas
        hotel_mapping = {
            'ALBUFEIRA SOL': 'ALBUFEIRA SOL',
            'APARTAMENTOS CABRITA': 'APARTAMENTOS CABRITA',
            'AQUAMAR': 'AQUAMAR',
            'CERRO MAR GARDEM': 'CERRO MAR GARDEM',
            'CLUBE MARIA LUISA': 'CLUBE MARIA LUISA',
            'EPIC SANA': 'EPIC SANA',
            'EXPOSE I': 'EXPOSE I',
            'FALESIA HOTEL': 'FALESIA HOTEL',
            'HOLIDAY IN (REAL BELA VISTA)': 'HOLIDAY IN (REAL BELA VISTA)',
            'INATEL': 'INATEL',
            'MASANA': 'MASANA',
            'OCEANUS': 'OCEANUS',
            'OURA ATLANTICO': 'OURA ATLANTICO',
            'OURA VIEW BEACH CLUB': 'OURA VIEW BEACH CLUB',
            'PALADIM': 'PALADIM',
            'PATEO VILLAGE': 'PATEO VILLAGE',
            'PATIO SUITE HOTEL': 'PATIO SUITE HOTEL',
            'PTO': 'PTO',
            'ROCAMAR': 'ROCAMAR',
            'SOL E MAR': 'SOL E MAR',
            'ZEBRA SAFARIS II': 'ZEBRA SAFARIS II'
        }
        
        # Buscar todos os comissionistas
        cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
        commissioners = {row[1].upper(): row[0] for row in cursor.fetchall()}
        
        total_updated = 0
        
        # Processar cada mês de 2025
        for month in range(1, 13):
            filename = f'cm-25/CM-{month:02d}-2025.xlsx'
            
            if not os.path.exists(filename):
                continue
            
            print(f"\n📄 Processando {filename}...")
            df = pd.read_excel(filename)
            
            current_hotel = None
            updated_count = 0
            
            for idx, row in df.iterrows():
                # Identificar nome do hotel
                if pd.notna(row.get('Voucher')) and pd.isna(row.get('Data Entrega')):
                    current_hotel = str(row['Voucher']).strip().upper()
                    continue
                
                # Processar reserva
                if pd.notna(row.get('Data Entrega')) and current_hotel:
                    try:
                        # Buscar ID do comissionista
                        commissioner_id = None
                        for hotel_name, comm_name in hotel_mapping.items():
                            if hotel_name.upper() in current_hotel:
                                commissioner_id = commissioners.get(comm_name.upper())
                                break
                        
                        if not commissioner_id:
                            continue
                        
                        # Extrair dados
                        pickup_date = pd.to_datetime(row['Data Entrega'])
                        days = int(row['Dias']) if pd.notna(row.get('Dias')) else 1
                        
                        # Verificar se há voucher manual
                        manual_voucher = None
                        if pd.notna(row.get('Voucher')):
                            voucher_str = str(row['Voucher']).strip()
                            if voucher_str and voucher_str != 'nan' and voucher_str.upper() != current_hotel:
                                manual_voucher = voucher_str
                        
                        # Calcular dropoff date
                        dropoff_date = pickup_date + timedelta(days=days)
                        
                        # Atualizar registro na base de dados
                        if manual_voucher:
                            cursor.execute("""
                                UPDATE commission_bookings
                                SET dropoff_date = %s
                                WHERE voucher_number = %s
                                  AND pickup_date = %s
                                  AND dropoff_date = pickup_date
                            """, (dropoff_date.date(), manual_voucher, pickup_date.date()))
                        else:
                            cursor.execute("""
                                UPDATE commission_bookings
                                SET dropoff_date = %s
                                WHERE ctid = (
                                    SELECT ctid
                                    FROM commission_bookings
                                    WHERE commissioner_id = %s
                                      AND pickup_date = %s
                                      AND dropoff_date = pickup_date
                                      AND voucher_number IS NULL
                                    LIMIT 1
                                )
                            """, (dropoff_date.date(), commissioner_id, pickup_date.date()))
                        
                        if cursor.rowcount > 0:
                            updated_count += 1
                            
                    except Exception as e:
                        print(f"  ⚠️  Erro linha {idx}: {e}")
                        conn.rollback()
                        continue
            
            conn.commit()
            print(f"  ✅ {updated_count} registos atualizados")
            total_updated += updated_count
        
        print("\n" + "=" * 80)
        print(f"✅ Atualização concluída!")
        print(f"  - Total de registos atualizados: {total_updated}")
        print("=" * 80)
        
        # Verificar quantos ainda têm o problema
        cursor.execute("""
            SELECT COUNT(*) 
            FROM commission_bookings 
            WHERE EXTRACT(YEAR FROM pickup_date) = 2025
              AND dropoff_date = pickup_date
        """)
        remaining = cursor.fetchone()[0]
        
        if remaining > 0:
            print(f"\n⚠️  Ainda existem {remaining} registos de 2025 com dropoff_date = pickup_date")
        else:
            print(f"\n✅ Todos os registos de 2025 foram corrigidos!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = fix_2025_from_excel()
    exit(0 if success else 1)
