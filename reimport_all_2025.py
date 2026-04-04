#!/usr/bin/env python3
"""
Reimportar TODOS os meses de 2025 da pasta 2025/
Com cálculo correto de dropoff_date
"""
import os
import pandas as pd
import psycopg2
from urllib.parse import urlparse
from datetime import datetime, timedelta

def import_all_2025():
    """Importa todos os meses de 2025"""
    
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
        
        # Buscar todos os comissionistas
        cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
        commissioners = {row[1].upper(): row[0] for row in cursor.fetchall()}
        
        print(f"\n📋 Comissionistas na base de dados: {len(commissioners)}")
        
        total_imported = 0
        total_skipped = 0
        
        # Processar cada mês
        for month in range(1, 13):
            filename = f'2025/CM-{month:02d}-2025.xlsx'
            
            if not os.path.exists(filename):
                print(f"\n⚠️  {filename} não encontrado")
                continue
            
            print(f"\n📄 Processando {filename}...")
            df = pd.read_excel(filename)
            
            current_hotel = None
            month_imported = 0
            month_skipped = 0
            
            for idx, row in df.iterrows():
                # Identificar nome do hotel (linhas com voucher preenchido mas sem data)
                if pd.notna(row.get('Voucher')) and pd.isna(row.get('Data Entrega')):
                    current_hotel = str(row['Voucher']).strip().upper()
                    continue
                
                # Processar reserva (linhas com data)
                if pd.notna(row.get('Data Entrega')) and current_hotel:
                    # Buscar ID do comissionista
                    commissioner_id = commissioners.get(current_hotel)
                    
                    if not commissioner_id:
                        month_skipped += 1
                        continue
                    
                    try:
                        # Extrair dados
                        pickup_date = pd.to_datetime(row['Data Entrega'])
                        days = int(row['Dias']) if pd.notna(row.get('Dias')) else 1
                        
                        # Obter base_price - pode estar em 'Preço Base' ou 'Loyalty Card'
                        base_price = 0
                        if 'Preço Base' in row and pd.notna(row['Preço Base']):
                            base_price_str = str(row['Preço Base']).replace(',', '.')
                            try:
                                base_price = float(base_price_str)
                            except:
                                base_price = 0
                        elif 'Loyalty Card' in row and pd.notna(row['Loyalty Card']):
                            base_price_str = str(row['Loyalty Card']).replace(',', '.')
                            try:
                                base_price = float(base_price_str)
                            except:
                                base_price = 0
                        
                        # Calcular comissão: (base_price / 1.23) * 0.15
                        commission_amount = (base_price / 1.23) * 0.15
                        
                        # Verificar se há voucher manual (só se for diferente do nome do hotel)
                        manual_voucher = None
                        if pd.notna(row.get('Voucher')):
                            voucher_str = str(row['Voucher']).strip()
                            if voucher_str and voucher_str != 'nan' and voucher_str.upper() != current_hotel:
                                manual_voucher = voucher_str
                        
                        # Calcular dropoff date
                        dropoff_date = pickup_date + timedelta(days=days)
                        
                        # Inserir reserva - permitir vouchers duplicados
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
                        
                        month_imported += 1
                        
                    except Exception as e:
                        print(f"  ❌ Erro linha {idx}: {e}")
                        month_skipped += 1
            
            conn.commit()
            print(f"  ✅ {month_imported} importadas, {month_skipped} ignoradas")
            total_imported += month_imported
            total_skipped += month_skipped
        
        print("\n" + "=" * 80)
        print(f"✅ Importação 2025 concluída!")
        print(f"  - Total importado: {total_imported}")
        print(f"  - Total ignorado: {total_skipped}")
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
    success = import_all_2025()
    exit(0 if success else 1)
