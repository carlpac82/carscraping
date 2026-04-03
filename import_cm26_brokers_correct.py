#!/usr/bin/env python3
"""
Script para importar dados de brokers CM-26 com MAPEAMENTO CORRETO
"""
import os
import psycopg2
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime

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

def import_cm26_brokers_correct():
    """Importar dados de brokers dos ficheiros CM-26 com mapeamento CORRETO"""
    print("=" * 80)
    print("IMPORTAÇÃO DE DADOS DE BROKERS CM-26 - MAPEAMENTO CORRETO")
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
        
        # Limpar dados incorretos anteriores
        cursor.execute("DELETE FROM broker_bookings")
        conn.commit()
        print("🧹 Dados anteriores limpos")
        
        # Mapeamento CORRETO de brokers (baseado na análise correta)
        broker_mapping = {
            'ABBYCAR-POA': 245,
            'ABBYCAR-PREPAID': 236,
            'AP': 157,
            'API-WEB': 200,
            'API': 200,  # Usar API-WEB
            'BROKERS - DIRECTOS': 252,
            'CARALLIANCE-POA': 253,
            'CARALLIANCE-PREPAID': 254,
            'CARJET-PREPAID': 237,
            'CARJET': 237,  # Usar CARJET-PREPAID
            'DISCOVERCARS-PREPAID': 246,
            'DISCOVERCARS-POA': 235,
            'RENTALCARS': 191,
            'VIP CARS-POA': 232,
            'VIP CARS': 232  # Usar VIP CARS-POA
        }
        
        # Ficheiros a processar
        files = [
            ('CM-26/CM-01-2026.xlsx', 'Janeiro'),
            ('CM-26/CM-02-2026.xlsx', 'Fevereiro'),
            ('CM-26/CM-03-2026.xlsx', 'Março')
        ]
        
        total_imported = 0
        total_errors = 0
        skipped_hotels = 0
        
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
                    
                    # Se temos um broker atual e esta linha tem dados válidos
                    if current_broker and current_broker_id and voucher.isdigit():
                        # Extrair dados da reserva
                        pickup_date = row['Data Entrega']
                        days = row['Dias']
                        total_price = row['Loyalty Card']
                        
                        if pd.notna(pickup_date) and pd.notna(days) and pd.notna(total_price):
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
                                        int(days),
                                        float(total_price),
                                        'confirmed',
                                        datetime.now()
                                    ))
                                    
                                    booking_id = cursor.fetchone()[0]
                                    conn.commit()
                                    print(f"    ✅ Importado: {voucher} - {current_broker} - {pickup_date.date()} - {days} dias - €{total_price}")
                                    total_imported += 1
                                else:
                                    print(f"    ⚠ Já existe: {voucher} - {current_broker}")
                                    
                            except Exception as e:
                                print(f"    ❌ Erro ao inserir {voucher}: {e}")
                                total_errors += 1
                        else:
                            # Dados incompletos - ignorar
                            pass
                    elif current_broker is None and voucher and not voucher.isdigit():
                        # É um hotel/não-broker - ignorar
                        skipped_hotels += 1
                                
            except Exception as e:
                print(f"  ❌ Erro ao processar {file_path}: {e}")
                total_errors += 1
        
        # Resumo final
        print(f"\n" + "=" * 80)
        print("RESUMO DA IMPORTAÇÃO CORRETA")
        print("=" * 80)
        print(f"✅ Total de registros importados: {total_imported}")
        print(f"❌ Total de erros: {total_errors}")
        print(f"⏭️ Hotéis/não-brokers ignorados: {skipped_hotels}")
        
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
        else:
            print("\n📊 Nenhum dado importado")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import_cm26_brokers_correct()
