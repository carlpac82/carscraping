#!/usr/bin/env python3
"""
Script para corrigir dropoff_date nas commission_bookings
Calcula dropoff_date = pickup_date + dias (lidos do Excel)
"""
import os
import pandas as pd
import psycopg2
from urllib.parse import urlparse
from datetime import datetime, timedelta

def fix_dropoff_dates():
    """Atualiza dropoff_date baseado nos dias dos ficheiros Excel"""
    
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
        
        # Ficheiros Excel a processar
        excel_files = [
            ('CM-01-2026.xlsx', 1, 2026),  # Janeiro 2026
            ('CM-02-2026.xlsx', 2, 2026),  # Fevereiro 2026
            ('CM-03-2026.xlsx', 3, 2026),  # Março 2026
        ]
        
        total_updated = 0
        
        for filename, month, year in excel_files:
            if not os.path.exists(filename):
                print(f"\n⚠️  Ficheiro {filename} não encontrado, a saltar...")
                continue
            
            print(f"\n📄 Processando {filename}...")
            df = pd.read_excel(filename)
            
            # Mapeamento de nomes de hotéis para comissionistas
            hotel_mapping = {
                'CERRO MAR GARDEM': 'CERRO MAR GARDEM',
                'CLUBE MARIA LUISA': 'CLUBE MARIA LUISA',
                'DISCOVERCARS-PREPAID': 'DISCOVERCARS-PREPAID',
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
            
            # Processar dados do Excel
            current_hotel = None
            updated_count = 0
            
            for idx, row in df.iterrows():
                # Identificar nome do hotel
                if pd.notna(row['Voucher']) and pd.isna(row['Data Entrega']):
                    current_hotel = row['Voucher'].strip().upper()
                    continue
                
                # Processar reserva
                if pd.notna(row['Data Entrega']) and current_hotel:
                    # Buscar ID do comissionista
                    commissioner_id = None
                    for hotel_name, comm_name in hotel_mapping.items():
                        if hotel_name in current_hotel:
                            commissioner_id = commissioners.get(comm_name.upper())
                            break
                    
                    if not commissioner_id:
                        continue
                    
                    # Extrair dados
                    pickup_date = pd.to_datetime(row['Data Entrega'])
                    days = int(row['Dias']) if pd.notna(row['Dias']) else 1
                    
                    # Verificar se há voucher manual
                    manual_voucher = None
                    if pd.notna(row['Voucher']):
                        voucher_str = str(row['Voucher']).strip()
                        if voucher_str and voucher_str != 'nan':
                            manual_voucher = voucher_str
                    
                    # Calcular dropoff date
                    dropoff_date = pickup_date + timedelta(days=days)
                    
                    # Atualizar registro na base de dados
                    try:
                        # Encontrar o registro correspondente
                        if manual_voucher:
                            cursor.execute("""
                                UPDATE commission_bookings
                                SET dropoff_date = %s
                                WHERE commissioner_id = %s
                                  AND voucher_number = %s
                                  AND pickup_date = %s
                                  AND (dropoff_date IS NULL OR dropoff_date = pickup_date)
                            """, (dropoff_date.date(), commissioner_id, manual_voucher, pickup_date.date()))
                        else:
                            # Para registos sem voucher, usar ctid para atualizar apenas o primeiro
                            cursor.execute("""
                                UPDATE commission_bookings
                                SET dropoff_date = %s
                                WHERE ctid = (
                                    SELECT ctid
                                    FROM commission_bookings
                                    WHERE commissioner_id = %s
                                      AND voucher_number IS NULL
                                      AND pickup_date = %s
                                      AND (dropoff_date IS NULL OR dropoff_date = pickup_date)
                                    LIMIT 1
                                )
                            """, (dropoff_date.date(), commissioner_id, pickup_date.date()))
                        
                        if cursor.rowcount > 0:
                            updated_count += 1
                            
                    except Exception as e:
                        print(f"  ❌ Erro ao atualizar {pickup_date.strftime('%d/%m/%Y')}: {e}")
                        conn.rollback()  # Rollback em caso de erro
                        continue
            
            conn.commit()
            print(f"  ✅ {updated_count} registos atualizados em {filename}")
            total_updated += updated_count
        
        print("\n" + "=" * 80)
        print(f"✅ Atualização concluída!")
        print(f"  - Total de registos atualizados: {total_updated}")
        print("=" * 80)
        
        # Verificar quantos ainda têm dropoff_date NULL ou igual a pickup_date
        cursor.execute("""
            SELECT COUNT(*) 
            FROM commission_bookings 
            WHERE dropoff_date IS NULL OR dropoff_date = pickup_date
        """)
        remaining = cursor.fetchone()[0]
        
        if remaining > 0:
            print(f"\n⚠️  Ainda existem {remaining} registos sem dropoff_date correto")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = fix_dropoff_dates()
    exit(0 if success else 1)
