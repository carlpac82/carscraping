#!/usr/bin/env python3
"""
Script para analisar e mostrar os erros da importação de 2025
"""
import os
import psycopg2
import pandas as pd
from urllib.parse import urlparse

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

def analyze_import_errors():
    """Analisar erros da importação"""
    print("=" * 80)
    print("ANÁLISE DE ERROS - IMPORTAÇÃO 2025")
    print("=" * 80)
    
    database_url = get_database_url()
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return
    
    result = urlparse(database_url)
    
    try:
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        
        # 1. Verificar comissionistas na base de dados
        cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
        commissioners = {row[1].upper(): row[0] for row in cursor.fetchall()}
        print(f"\n📋 Comissionistas na base de dados: {len(commissioners)}")
        
        # 2. Mapeamento usado na importação
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
        
        print(f"\n🗺️  Mapeamento de hotéis para comissionistas: {len(hotel_mapping)}")
        
        # 3. Analisar todos os arquivos Excel para encontrar hotéis não mapeados
        import glob
        excel_files = sorted(glob.glob("/Users/filipepacheco/CascadeProjects/carscraping/2025/CM-*.xlsx"))
        
        all_hotels_found = set()
        unmapped_hotels = set()
        missing_commissioners = set()
        
        print(f"\n📁 Analisando {len(excel_files)} arquivos...")
        
        for file_path in excel_files:
            filename = file_path.split('/')[-1]
            print(f"\n📄 {filename}:")
            
            df = pd.read_excel(file_path)
            current_hotel = None
            
            for idx, row in df.iterrows():
                # Identificar nome do hotel
                if pd.notna(row['Voucher']) and pd.isna(row['Data Entrega']):
                    current_hotel = row['Voucher'].strip().upper()
                    all_hotels_found.add(current_hotel)
                    
                    # Verificar se está mapeado
                    is_mapped = False
                    for hotel_name, comm_name in hotel_mapping.items():
                        if hotel_name in current_hotel:
                            # Verificar se o comissionista existe
                            if comm_name.upper() in commissioners:
                                is_mapped = True
                            else:
                                missing_commissioners.add(comm_name)
                                is_mapped = False
                            break
                    
                    if not is_mapped:
                        unmapped_hotels.add(current_hotel)
                        print(f"  ❌ {current_hotel} - NÃO MAPEADO")
                    else:
                        print(f"  ✅ {current_hotel} - Mapeado")
        
        print(f"\n" + "=" * 80)
        print("RESUMO DOS ERROS:")
        print("=" * 80)
        
        print(f"\n🏨 Total de hotéis encontrados: {len(all_hotels_found)}")
        print(f"🗺️  Hotéis mapeados: {len(all_hotels_found) - len(unmapped_hotels)}")
        print(f"❌ Hotéis NÃO mapeados: {len(unmapped_hotels)}")
        
        if unmapped_hotels:
            print(f"\n📋 Hotéis sem mapeamento:")
            for hotel in sorted(unmapped_hotels):
                print(f"  - {hotel}")
        
        if missing_commissioners:
            print(f"\n👥 Comissionistas mapeados mas não existentes na BD:")
            for comm in sorted(missing_commissioners):
                print(f"  - {comm}")
        
        # 4. Verificar dados importados
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN pickup_date >= '2025-01-01' AND pickup_date < '2026-01-01' THEN 1 ELSE 0 END) as imported_2025
            FROM commission_bookings
        """)
        result = cursor.fetchone()
        
        print(f"\n📊 Estatísticas da importação:")
        print(f"  - Total de reservas na BD: {result[0]}")
        print(f"  - Reservas de 2025 importadas: {result[1]}")
        
        # 5. Mostrar exemplos de reservas importadas
        cursor.execute("""
            SELECT cb.commissioner_id, c.name, cb.pickup_date, cb.price, cb.commission_amount
            FROM commission_bookings cb
            LEFT JOIN commissioners c ON cb.commissioner_id = c.id
            WHERE cb.pickup_date >= '2025-01-01' AND cb.pickup_date < '2026-01-01'
            ORDER BY cb.pickup_date DESC
            LIMIT 10
        """)
        
        examples = cursor.fetchall()
        if examples:
            print(f"\n💡 Exemplos de reservas importadas:")
            for ex in examples:
                print(f"  - {ex[1]}: {ex[2]} - Total: €{ex[3]:.2f} - Comissão: €{ex[4]:.2f}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    analyze_import_errors()
