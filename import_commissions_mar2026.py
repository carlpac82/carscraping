#!/usr/bin/env python3
"""
Script para importar comissões de março 2026 do ficheiro CM-03-2026.xlsx
"""
import os
import pandas as pd
import psycopg2
from urllib.parse import urlparse
from datetime import datetime, timedelta

def import_commissions():
    """Importa comissões do Excel para a base de dados"""
    
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
        
        # Ler ficheiro Excel
        print("\n📄 Lendo ficheiro CM-03-2026.xlsx...")
        df = pd.read_excel('CM-03-2026.xlsx')
        
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
        
        print(f"\n📋 Comissionistas na base de dados: {len(commissioners)}")
        
        # Processar dados do Excel
        current_hotel = None
        imported_count = 0
        skipped_count = 0
        
        print("\n📝 Importando reservas...")
        
        for idx, row in df.iterrows():
            # Identificar nome do hotel (linhas com voucher preenchido mas sem data)
            if pd.notna(row['Voucher']) and pd.isna(row['Data Entrega']):
                current_hotel = row['Voucher'].strip().upper()
                print(f"\n🏨 {current_hotel}")
                continue
            
            # Processar reserva (linhas com data)
            if pd.notna(row['Data Entrega']) and current_hotel:
                # Buscar ID do comissionista
                commissioner_id = None
                for hotel_name, comm_name in hotel_mapping.items():
                    if hotel_name in current_hotel:
                        commissioner_id = commissioners.get(comm_name.upper())
                        break
                
                if not commissioner_id:
                    print(f"  ⚠️  Comissionista '{current_hotel}' não encontrado na base de dados")
                    skipped_count += 1
                    continue
                
                # Extrair dados
                pickup_date = pd.to_datetime(row['Data Entrega'])
                days = int(row['Dias']) if pd.notna(row['Dias']) else 1
                
                # Tratar valores com vírgula (ex: 23,76) - ESTE É O BASE_PRICE
                base_price_str = str(row['Loyalty Card']).replace(',', '.')
                try:
                    base_price = float(base_price_str)
                except:
                    base_price = 0
                
                # Calcular comissão corretamente: (base_price / 1.23) * 0.15
                commission_amount = (base_price / 1.23) * 0.15
                
                # Verificar se há voucher manual
                manual_voucher = None
                if pd.notna(row['Voucher']):
                    voucher_str = str(row['Voucher']).strip()
                    if voucher_str and voucher_str != 'nan':
                        manual_voucher = voucher_str
                
                # Calcular dropoff date
                dropoff_date = pickup_date + timedelta(days=days)
                
                # Inserir reserva
                try:
                    cursor.execute("""
                        INSERT INTO commission_bookings (
                            commissioner_id, voucher_number, client_name, client_email, client_phone,
                            pickup_date, pickup_time, dropoff_date, dropoff_time,
                            pickup_location, dropoff_location, vehicle_group, extras,
                            price, base_price, deposit, status, commission_rate, commission_amount,
                            created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """, (
                        commissioner_id, manual_voucher, 'Loyalty Card', '', '',
                        pickup_date.date(), pickup_date.strftime('%H:%M'), 
                        dropoff_date.date(), '00:00',
                        '', '', '', '[]',
                        base_price, base_price, 0, 'confirmed', 15.0, commission_amount
                    ))
                    
                    voucher_str = f" (voucher: {manual_voucher})" if manual_voucher else ""
                    print(f"  ✅ {pickup_date.strftime('%d/%m/%Y')} - {days} dias - €{commission_amount:.2f}{voucher_str}")
                    imported_count += 1
                    
                except Exception as e:
                    print(f"  ❌ Erro ao importar: {e}")
                    skipped_count += 1
        
        conn.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Importação concluída!")
        print(f"  - Reservas importadas: {imported_count}")
        print(f"  - Reservas ignoradas: {skipped_count}")
        print("=" * 80)
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = import_commissions()
    exit(0 if success else 1)
