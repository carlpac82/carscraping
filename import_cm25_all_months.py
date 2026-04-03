#!/usr/bin/env python3
"""
Script para importar TODOS os meses de 2025 (Janeiro a Dezembro)
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

def import_month(cursor, conn, month_num, year, broker_mapping):
    """Importar um mês específico"""
    month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    file_path = f'CM-25/CM-{month_num:02d}-{year}.xlsx'
    
    if not os.path.exists(file_path):
        print(f"❌ Ficheiro não encontrado: {file_path}")
        return 0, 0
    
    print(f"\n{'='*80}")
    print(f"📅 IMPORTANDO {month_names[month_num-1].upper()} {year}")
    print(f"{'='*80}")
    
    df = pd.read_excel(file_path)
    
    total_imported = 0
    total_errors = 0
    
    # Variável para controlar o broker atual
    current_broker = None
    current_broker_id = None
    
    for idx, row in df.iterrows():
        voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
        pickup_date_raw = row['Data Entrega']
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
            # Converter data se necessário
            if pd.notna(pickup_date_raw):
                try:
                    if isinstance(pickup_date_raw, str):
                        if 'T' in pickup_date_raw:
                            pickup_date = datetime.fromisoformat(pickup_date_raw.replace('Z', '+00:00'))
                        else:
                            pickup_date = datetime.strptime(pickup_date_raw, '%Y-%m-%d')
                    else:
                        pickup_date = pickup_date_raw
                except:
                    continue
            else:
                continue
            
            # Importar se tiver dados válidos (mesmo com voucher vazio ou especial)
            if pd.notna(days) and total_price is not None and total_price > 0:
                # Verificar se é do mês e ano corretos
                if pickup_date.month == month_num and pickup_date.year == year:
                    try:
                        # Gerar voucher único se estiver vazio ou for especial
                        if voucher and voucher.isdigit():
                            voucher_final = voucher
                        else:
                            # Para vouchers especiais, gerar um único
                            voucher_final = f"{current_broker}-{year}-{month_num:02d}-{idx}"
                        
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
                            total_imported += 1
                        
                    except Exception as e:
                        print(f"    ❌ Erro ao inserir linha {idx}: {e}")
                        total_errors += 1
    
    print(f"\n✅ {month_names[month_num-1]}: {total_imported} reservas importadas, {total_errors} erros")
    return total_imported, total_errors

def import_all_2025():
    print("=" * 80)
    print("IMPORTAÇÃO COMPLETA DE 2025 (JANEIRO A DEZEMBRO)")
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
        
        # Remover todos os dados de 2025
        cursor.execute("DELETE FROM broker_bookings WHERE EXTRACT(YEAR FROM pickup_date) = 2025")
        deleted_count = cursor.rowcount
        conn.commit()
        print(f"🧹 Removidos {deleted_count} registros de 2025")
        
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
        
        # Importar todos os 12 meses
        total_year_imported = 0
        total_year_errors = 0
        
        for month in range(1, 13):
            imported, errors = import_month(cursor, conn, month, 2025, broker_mapping)
            total_year_imported += imported
            total_year_errors += errors
        
        # Resumo final
        print(f"\n" + "=" * 80)
        print("RESUMO FINAL - ANO 2025 COMPLETO")
        print("=" * 80)
        print(f"✅ Total de registros importados: {total_year_imported}")
        print(f"❌ Total de erros: {total_year_errors}")
        
        # Verificar totais por mês
        cursor.execute('''
            SELECT 
                EXTRACT(MONTH FROM pickup_date) as mes,
                COUNT(*) as total,
                SUM(total_price) as valor_total
            FROM broker_bookings 
            WHERE EXTRACT(YEAR FROM pickup_date) = 2025
            GROUP BY EXTRACT(MONTH FROM pickup_date)
            ORDER BY mes
        ''')
        
        month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                       'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        months_summary = cursor.fetchall()
        if months_summary:
            print(f"\n📊 Distribuição por mês (2025):")
            for month, count, total in months_summary:
                print(f"  📅 {month_names[int(month)-1]}: {count} reservas, €{total:.2f}")
        
        # Verificar totais por broker
        cursor.execute('''
            SELECT broker_name, COUNT(*) as total, SUM(total_price) as valor_total
            FROM broker_bookings 
            WHERE EXTRACT(YEAR FROM pickup_date) = 2025
            GROUP BY broker_name 
            ORDER BY total DESC
        ''')
        
        brokers_summary = cursor.fetchall()
        if brokers_summary:
            print(f"\n📊 Distribuição por broker (2025):")
            for broker, count, total in brokers_summary:
                print(f"  🏢 {broker}: {count} reservas, €{total:.2f}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import_all_2025()
