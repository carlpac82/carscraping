#!/usr/bin/env python3
"""
Script para importar dados de comissões de 2025 dos arquivos Excel
Processo igual ao usado ontem para 2026
"""
import os
import psycopg2
import pandas as pd
from urllib.parse import urlparse
from datetime import timedelta

def get_database_url():
    """Obter DATABASE_URL do ficheiro .env"""
    database_url = None
    
    # Tentar ler do ficheiro .env
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    database_url = line.split('=', 1)[1].strip()
                    break
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return None
    
    return database_url

def import_monthly_commissions(file_path, month, year):
    """Importar comissões de um arquivo mensal"""
    print(f"\n📄 Processando {file_path}...")
    
    database_url = get_database_url()
    if not database_url:
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
        
        # Mapeamento de nomes de hotéis para comissionistas (igual ao de 2026)
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
        
        print(f"📋 Comissionistas na base de dados: {len(commissioners)}")
        
        # Ler ficheiro Excel
        df = pd.read_excel(file_path)
        print(f"📊 Arquivo lido: {len(df)} linhas")
        
        # Processar dados do Excel
        current_hotel = None
        imported_count = 0
        skipped_count = 0
        
        print("📝 Importando reservas...")
        
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
                
                # Tratar valores com vírgula (ex: 23,76)
                loyalty_card_str = str(row['Loyalty Card']).replace(',', '.')
                try:
                    loyalty_card_amount = float(loyalty_card_str)
                except:
                    loyalty_card_amount = 0
                
                # Verificar se há voucher manual
                manual_voucher = None
                if pd.notna(row['Voucher']):
                    voucher_str = str(row['Voucher']).strip()
                    if voucher_str and voucher_str != 'nan':
                        manual_voucher = voucher_str
                
                # Calcular dropoff date
                dropoff_date = pickup_date + timedelta(days=days)
                
                # Cálculo correto das comissões:
                # 1. loyalty_card_amount é o valor total com IVA (23%)
                # 2. Calcular valor líquido (sem IVA): loyalty_card_amount / 1.23
                # 3. Calcular comissão (15% do valor líquido): (loyalty_card_amount / 1.23) * 0.15
                base_price = loyalty_card_amount  # Preço total com IVA
                net_price = base_price / 1.23  # Valor sem IVA
                commission_amount = net_price * 0.15  # 15% comissão
                
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
                        '', '', 'LOYALTY', '[]',
                        base_price, base_price, 0, 'confirmed', 15.0, commission_amount
                    ))
                    
                    voucher_str = f" (voucher: {manual_voucher})" if manual_voucher else ""
                    print(f"  ✅ {pickup_date.strftime('%d/%m/%Y')} - {days} dias - Total: €{base_price:.2f} - Comissão: €{commission_amount:.2f}{voucher_str}")
                    imported_count += 1
                    
                except Exception as e:
                    print(f"  ❌ Erro ao importar: {e}")
                    skipped_count += 1
        
        conn.commit()
        
        print(f"\n✅ Mês {month:02d}/{year}:")
        print(f"  - Reservas importadas: {imported_count}")
        print(f"  - Reservas ignoradas: {skipped_count}")
        
        cursor.close()
        conn.close()
        return imported_count
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return 0

def main():
    """Função principal"""
    print("=" * 80)
    print("IMPORTAÇÃO DE COMISSÕES 2025 - PROCESSO COMPLETO")
    print("=" * 80)
    
    # Diretório dos arquivos
    import glob
    excel_files = sorted(glob.glob("/Users/filipepacheco/CascadeProjects/carscraping/2025/CM-*.xlsx"))
    
    if not excel_files:
        print("❌ Nenhum arquivo encontrado!")
        return
    
    print(f"📁 Encontrados {len(excel_files)} arquivos:")
    for file_path in excel_files:
        print(f"  - {file_path.split('/')[-1]}")
    
    # Limpar dados existentes de 2025
    print("\n🧹 Limpando dados existentes de 2025...")
    database_url = get_database_url()
    if database_url:
        result = urlparse(database_url)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        cursor.execute("DELETE FROM commission_bookings WHERE pickup_date >= '2025-01-01' AND pickup_date < '2026-01-01'")
        deleted = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        print(f"  🗑️  Removidos {deleted} registros de 2025")
    
    # Importar todos os meses
    total_imported = 0
    for file_path in excel_files:
        # Extrair mês e ano do nome do arquivo
        filename = file_path.split('/')[-1]
        parts = filename.replace('.xlsx', '').split('-')
        if len(parts) >= 3:
            month = int(parts[1])
            year = int(parts[2])
            
            count = import_monthly_commissions(file_path, month, year)
            total_imported += count
    
    print("\n" + "=" * 80)
    print(f"✅ Importação concluída!")
    print(f"  - Total de reservas importadas: {total_imported}")
    print("=" * 80)

if __name__ == "__main__":
    main()
