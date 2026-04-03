#!/usr/bin/env python3
"""
Script para importar as reservas faltantes do broker AP
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

def import_ap_missing():
    print("=" * 80)
    print("IMPORTAÇÃO DAS RESERVAS FALTANTES DO BROKER AP")
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
        
        # Remover apenas as reservas do AP de Fevereiro 2026
        cursor.execute("DELETE FROM broker_bookings WHERE broker_name = 'AP' AND EXTRACT(MONTH FROM pickup_date) = 2 AND EXTRACT(YEAR FROM pickup_date) = 2026")
        conn.commit()
        print("🧹 Reservas do AP de Fevereiro 2026 removidas")
        
        # Processar ficheiro de Fevereiro
        file_path = 'CM-26/CM-02-2026.xlsx'
        df = pd.read_excel(file_path)
        
        # Encontrar broker AP
        ap_line = None
        for idx, row in df.iterrows():
            voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
            if voucher == 'AP':
                ap_line = idx
                break
        
        if ap_line is None:
            print("❌ Broker AP não encontrado!")
            return
        
        print(f"🏢 Broker AP encontrado na linha {ap_line}")
        
        total_imported = 0
        total_errors = 0
        
        # Processar linhas depois do AP até encontrar outro broker
        for idx in range(ap_line + 1, len(df)):
            row = df.iloc[idx]
            voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
            pickup_date = row['Data Entrega']
            days = row['Dias']
            total_price = normalize_price(row['Loyalty Card'])
            
            # Parar quando encontrar outro broker
            if voucher and not voucher.isdigit() and voucher != '' and voucher != 'nan':
                print(f"🛑 Parando - Outro broker encontrado: {voucher} na linha {idx}")
                break
            
            # Importar se tiver dados válidos (mesmo com voucher vazio)
            if pd.notna(pickup_date) and pd.notna(days) and total_price is not None and total_price > 0:
                # Verificar se é Fevereiro 2026
                if pickup_date.month == 2 and pickup_date.year == 2026:
                    try:
                        # Gerar voucher único se estiver vazio
                        voucher_final = voucher if voucher and voucher.isdigit() else f"AP-AP-{idx}"
                        
                        # Verificar se já existe
                        cursor.execute('''
                            SELECT id FROM broker_bookings 
                            WHERE voucher_number = %s AND broker_name = %s
                        ''', (voucher_final, 'AP'))
                        
                        if cursor.fetchone() is None:
                            # Inserir novo registro
                            cursor.execute('''
                                INSERT INTO broker_bookings 
                                (broker_name, voucher_number, client_name, pickup_date, dropoff_date, 
                                 vehicle_group, days, total_price, status, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                RETURNING id
                            ''', (
                                'AP',
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
                            print(f"    ✅ Importado: {voucher_final} - AP - {pickup_date.date()} - {days} dias - €{total_price:.2f}")
                            total_imported += 1
                        else:
                            print(f"    ⚠ Já existe: {voucher_final} - AP")
                            
                    except Exception as e:
                        print(f"    ❌ Erro ao inserir linha {idx}: {e}")
                        total_errors += 1
        
        # Resumo final
        print(f"\n" + "=" * 80)
        print("RESUMO DA IMPORTAÇÃO - BROKER AP")
        print("=" * 80)
        print(f"✅ Total de registros importados: {total_imported}")
        print(f"❌ Total de erros: {total_errors}")
        
        # Verificar totais
        cursor.execute('SELECT COUNT(*), SUM(total_price) FROM broker_bookings WHERE broker_name = %s AND EXTRACT(MONTH FROM pickup_date) = 2 AND EXTRACT(YEAR FROM pickup_date) = 2026', ('AP',))
        result = cursor.fetchone()
        print(f"📊 Total de reservas AP Fevereiro 2026: {result[0]}")
        print(f"💰 Valor total AP Fevereiro 2026: €{result[1] or 0:.2f}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import_ap_missing()
