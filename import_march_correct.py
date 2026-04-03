#!/usr/bin/env python3
"""
Script para importar Março 2026 CORRETAMENTE
"""
import os
import psycopg2
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime
import re

def get_database_url():
    database_url = None
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    database_url = line.split('=', 1)[1].strip()
                    break
    return database_url

def normalize_price(price_value):
    if pd.isna(price_value):
        return None
    price_str = str(price_value).strip()
    price_str = re.sub(r'[€\s]', '', price_str)
    price_str = price_str.replace(',', '.')
    if price_str.count('.') > 1:
        parts = price_str.split('.')
        price_str = ''.join(parts[:-1]) + '.' + parts[-1]
    try:
        return float(price_str)
    except ValueError:
        return None

def import_march_correct():
    print("=" * 80)
    print("IMPORTAÇÃO CORRETA DE MARÇO 2026")
    print("=" * 80)
    
    database_url = get_database_url()
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return
    
    result = urlparse(database_url)
    
    try:
        conn = psycopg2.connect(
            database="railway",
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        print("✅ Conectado à base de dados")
        
        # Remover todos os dados de Março 2026
        cursor.execute("DELETE FROM broker_bookings WHERE EXTRACT(MONTH FROM pickup_date) = 3 AND EXTRACT(YEAR FROM pickup_date) = 2026")
        conn.commit()
        print("🧹 Todos os dados de Março 2026 removidos")
        
        # Mapeamento CORRETO de brokers
        broker_mapping = {
            'ABBYCAR-POA': 245,
            'ABBYCAR-PREPAID': 236,
            'AP': 157,
            'API-WEB': 200,
            'API': 200,
            'BROKERS - DIRECTOS': 252,
            'CARALLIANCE-POA': 253,
            'CARALLIANCE-PREPAID': 254,
            'CARJET-PREPAID': 237,
            'CARJET': 237,
            'DISCOVERCARS-PREPAID': 246,
            'DISCOVERCARS-POA': 235,
            'RENTALCARS': 191,
            'VIP CARS-POA': 232,
            'VIP CARS': 232
        }
        
        # Processar ficheiro de Março
        file_path = 'CM-26/CM-03-2026.xlsx'
        df = pd.read_excel(file_path)
        
        total_imported = 0
        total_errors = 0
        
        # Variável para controlar o broker atual
        current_broker = None
        current_broker_id = None
        
        for idx, row in df.iterrows():
            voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
            pickup_date = row['Data Entrega']
            days = row['Dias']
            total_price = normalize_price(row['Loyalty Card'])
            
            # Verificar se é um broker válido
            if voucher in broker_mapping:
                current_broker = voucher
                current_broker_id = broker_mapping[voucher]
                print(f"  🏢 Broker encontrado: {current_broker} (ID: {current_broker_id})")
                continue
            
            # Se temos um broker atual
            if current_broker and current_broker_id:
                # Importar se tiver dados válidos (mesmo com voucher vazio ou especial)
                if pd.notna(pickup_date) and pd.notna(days) and total_price is not None and total_price > 0:
                    # Verificar se é Março 2026
                    if pickup_date.month == 3 and pickup_date.year == 2026:
                        try:
                            # Gerar voucher único se estiver vazio ou for especial
                            if voucher and voucher.isdigit():
                                voucher_final = voucher
                            else:
                                # Para vouchers especiais, gerar um único
                                voucher_final = f"{current_broker}-{idx}"
                            
                            # Verificar se já existe
                            cursor.execute('''
                                SELECT id FROM broker_bookings 
                                WHERE voucher_number = %s AND broker_name = %s
                            ''', (voucher_final, current_broker))
                            
                            if cursor.fetchone() is None:
                                # Inserir novo registro
                                cursor.execute('''
                                    INSERT INTO broker_bookings 
                                    (broker_name, voucher_number, client_name, pickup_date, dropoff_date, 
                                     vehicle_group, days, total_price, status, created_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    RETURNING id
                                ''', (
                                    current_broker,
                                    voucher_final,
                                    'N/A',
                                    pickup_date,
                                    pickup_date,
                                    'N/A',
                                    int(days) if pd.notna(days) else 0,
                                    total_price,
                                    'confirmed',
                                    datetime.now()
                                ))
                                
                                booking_id = cursor.fetchone()[0]
                                conn.commit()
                                print(f"    ✅ Importado: {voucher_final} - {current_broker} - {pickup_date.date()} - {days} dias - €{total_price:.2f}")
                                total_imported += 1
                            else:
                                print(f"    ⚠ Já existe: {voucher_final} - {current_broker}")
                                
                        except Exception as e:
                            print(f"    ❌ Erro ao inserir linha {idx}: {e}")
                            total_errors += 1
                                
            elif voucher and voucher != 'nan' and not voucher.isdigit():
                # É um hotel/não-broker - ignorar silenciosamente
                pass
        
        # Resumo final
        print(f"\n" + "=" * 80)
        print("RESUMO FINAL - MARÇO 2026 CORRETO")
        print("=" * 80)
        print(f"✅ Total de registros importados: {total_imported}")
        print(f"❌ Total de erros: {total_errors}")
        
        # Verificar totais
        cursor.execute('SELECT COUNT(*) FROM broker_bookings WHERE EXTRACT(MONTH FROM pickup_date) = 3 AND EXTRACT(YEAR FROM pickup_date) = 2026')
        total_db = cursor.fetchone()[0]
        print(f"📊 Total de broker_bookings Março 2026: {total_db}")
        
        # Mostrar distribuição
        cursor.execute('''
            SELECT broker_name, COUNT(*) as total, SUM(total_price) as valor_total
            FROM broker_bookings 
            WHERE EXTRACT(MONTH FROM pickup_date) = 3 AND EXTRACT(YEAR FROM pickup_date) = 2026
            GROUP BY broker_name 
            ORDER BY total DESC
        ''')
        
        brokers_summary = cursor.fetchall()
        if brokers_summary:
            print(f"\n📊 Distribuição Março 2026:")
            for broker, count, total in brokers_summary:
                print(f"  🏢 {broker}: {count} reservas, €{total:.2f}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import_march_correct()
