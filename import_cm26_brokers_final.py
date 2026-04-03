#!/usr/bin/env python3
"""
Script FINAL para importar TODOS os dados de brokers CM-26
"""
import os
import psycopg2
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime
import re

def get_database_url():
    """Obter DATABASE_URL do ficheiro .env"""
    database_url = None
    
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    database_url = line.split('=', 1)[1].strip()
                    break
    
    return database_url

def normalize_price(price_value):
    """Normalizar preço (aceitar pontos e vírgulas)"""
    if pd.isna(price_value):
        return None
    
    # Converter para string
    price_str = str(price_value).strip()
    
    # Remover espaços e símbolos de euro
    price_str = re.sub(r'[€\s]', '', price_str)
    
    # Substituir vírgula por ponto para casas decimais
    price_str = price_str.replace(',', '.')
    
    # Remover múltiplos pontos (manter apenas o último como decimal)
    if price_str.count('.') > 1:
        parts = price_str.split('.')
        price_str = ''.join(parts[:-1]) + '.' + parts[-1]
    
    try:
        return float(price_str)
    except ValueError:
        return None

def import_all_cm26_brokers():
    """Importar TODOS os dados de brokers dos ficheiros CM-26"""
    print("=" * 80)
    print("IMPORTAÇÃO COMPLETA DE DADOS DE BROKERS CM-26")
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
        
        # Limpar dados anteriores
        cursor.execute("DELETE FROM broker_bookings")
        conn.commit()
        print("🧹 Dados anteriores limpos")
        
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
        
        # Ficheiros a processar
        files = [
            ('CM-26/CM-01-2026.xlsx', 'Janeiro'),
            ('CM-26/CM-02-2026.xlsx', 'Fevereiro'),
            ('CM-26/CM-03-2026.xlsx', 'Março')
        ]
        
        total_imported = 0
        total_errors = 0
        total_skipped = 0
        
        for file_path, month_name in files:
            print(f"\n📄 Processando {file_path} - {month_name}...")
            
            try:
                # Ler Excel
                df = pd.read_excel(file_path)
                print(f"  📋 Linhas no arquivo: {len(df)}")
                
                # Variável para controlar o broker atual
                current_broker = None
                current_broker_id = None
                
                for idx, row in df.iterrows():
                    voucher = str(row['Voucher']) if pd.notna(row['Voucher']) else ''
                    
                    # Verificar se é um broker válido
                    if voucher in broker_mapping:
                        current_broker = voucher
                        current_broker_id = broker_mapping[voucher]
                        print(f"  🏢 Broker encontrado: {current_broker} (ID: {current_broker_id})")
                        continue
                    
                    # Se temos um broker atual
                    if current_broker and current_broker_id:
                        # Tentar extrair dados da reserva
                        pickup_date = row['Data Entrega']
                        days = row['Dias']
                        total_price = normalize_price(row['Loyalty Card'])
                        
                        # Verificar se temos dados mínimos
                        if pd.notna(pickup_date) and pd.notna(days) and total_price is not None and total_price > 0:
                            try:
                                # Verificar se já existe
                                cursor.execute('''
                                    SELECT id FROM broker_bookings 
                                    WHERE voucher_number = %s AND broker_name = %s
                                ''', (voucher, current_broker))
                                
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
                                        voucher,
                                        'N/A',  # Não disponível nos dados
                                        pickup_date,
                                        pickup_date,  # Mesma data, não disponível dropoff
                                        'N/A',  # Não disponível
                                        int(days) if pd.notna(days) else 0,
                                        total_price,
                                        'confirmed',
                                        datetime.now()
                                    ))
                                    
                                    booking_id = cursor.fetchone()[0]
                                    conn.commit()
                                    print(f"    ✅ Importado: {voucher} - {current_broker} - {pickup_date.date()} - {days} dias - €{total_price:.2f}")
                                    total_imported += 1
                                else:
                                    print(f"    ⚠ Já existe: {voucher} - {current_broker}")
                                    
                            except Exception as e:
                                print(f"    ❌ Erro ao inserir {voucher}: {e}")
                                total_errors += 1
                        else:
                            # Dados inválidos/incompletos - mostrar o que foi ignorado
                            if voucher and voucher != 'nan':
                                print(f"    ⏭️ Ignorado (dados inválidos): {voucher} - Data: {pickup_date} - Dias: {days} - Preço: {row['Loyalty Card']}")
                                total_skipped += 1
                    elif voucher and voucher != 'nan' and not voucher.isdigit():
                        # É um hotel/não-broker - ignorar silenciosamente
                        pass
                                
            except Exception as e:
                print(f"  ❌ Erro ao processar {file_path}: {e}")
                total_errors += 1
        
        # Resumo final
        print(f"\n" + "=" * 80)
        print("RESUMO FINAL DA IMPORTAÇÃO")
        print("=" * 80)
        print(f"✅ Total de registros importados: {total_imported}")
        print(f"❌ Total de erros: {total_errors}")
        print(f"⏭️ Total de ignorados (dados inválidos): {total_skipped}")
        
        # Verificar totais na base de dados
        cursor.execute('SELECT COUNT(*) FROM broker_bookings')
        total_db = cursor.fetchone()[0]
        print(f"📊 Total de broker_bookings na BD: {total_db}")
        
        # Mostrar distribuição por broker
        cursor.execute('''
            SELECT broker_name, COUNT(*) as total, SUM(total_price) as valor_total
            FROM broker_bookings 
            GROUP BY broker_name 
            ORDER BY total DESC
        ''')
        
        brokers_summary = cursor.fetchall()
        if brokers_summary:
            print(f"\n📊 Distribuição por broker:")
            for broker, count, total in brokers_summary:
                print(f"  🏢 {broker}: {count} reservas, €{total:.2f}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import_all_cm26_brokers()
