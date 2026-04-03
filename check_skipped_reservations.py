#!/usr/bin/env python3
"""
Script para verificar reservas ignoradas na importação de 2025
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

def check_skipped_reservations():
    """Verificar reservas ignoradas"""
    print("=" * 80)
    print("VERIFICAÇÃO DE RESERVAS IGNORADAS - 2025")
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
        
        # Mapeamento completo usado na importação
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
            'ZEBRA SAFARIS II': 'ZEBRA SAFARIS II',
            'ALBUFEIRA SOL': 'ALBUFEIRA SOL',
            'APARTAMENTOS CABRITA': 'APARTAMENTOS CABRITA',
            'AREIAS VILLAGE': 'AREIAS VILLAGE',
            'HOTEL BOAVISTA': 'HOTEL BOAVISTA',
            'HOTEL JUPITER': 'HOTEL JUPITER',
            'HOTEL CALIFORNIA': 'HOTEL CALIFORNIA',
            'PORTO BAY BLUE OCEAN': 'PORTO BAY BLUE OCEAN',
            'PORTO BAY FALESIA': 'PORTO BAY FALESIA',
            'VILA GALE PRAIA': 'VILA GALE PRAIA',
            'VILAS SÃO VICENTE': 'VILAS SÃO VICENTE',
            'ALFAGAR': 'ALFAGAR',
            'ALGARVE & COMPANHIA': 'ALGARVE & COMPANHIA',
            'ALGAVE MOTORHOME PARK': 'ALGAVE MOTORHOME PARK',
            'ALTO DA COLINA': 'ALTO DA COLINA',
            'AQUA PEDRA DOS BICOS': 'AQUA PEDRA DOS BICOS',
            'AQUAMAR': 'AQUAMAR',
            'BELA VISTA JARDIM II': 'BELA VISTA JARDIM II',
            'BORDA D´AGUA': 'BORDA D´AGUA',
            'BROKERS - DIRECTOS': 'BROKERS - DIRECTOS',
            'CLUB MED- EMMA': 'CLUB MED- EMMA',
            'CLUBE ALBUFEIRA': 'CLUBE ALBUFEIRA',
            'CLUBE MED - MANUELA': 'CLUBE MED - MANUELA',
            'JARDINS DE VALE DE PARRA': 'JARDINS DE VALE DE PARRA',
            'JOAO FERREIRA': 'JOAO FERREIRA',
            'KR HOTELS': 'KR HOTELS',
            'NAU SAO RAFAEL SUITES': 'NAU SAO RAFAEL SUITES',
            'NOVO CHORO': 'NOVO CHORO',
            'OCEAN VIEW': 'OCEAN VIEW',
            'PINHEIROS DA BALAIA': 'PINHEIROS DA BALAIA',
            'QUINTA PEDRA DOS BICOS': 'QUINTA PEDRA DOS BICOS',
            'REAL SANTA EULALIA': 'REAL SANTA EULALIA',
            'REGENCY SALGADOS': 'REGENCY SALGADOS',
            'SEM COMISSÃO': 'SEM COMISSÃO',
            'SUNCHINE RESTAURANTE': 'SUNCHINE RESTAURANTE',
            'TTO OLHOS DE AGUA': 'TTO OLHOS DE AGUA',
            'VALE CARRO': 'VALE CARRO',
            'VICTORIA': 'VICTORIA',
            'VILA GALE ATLANTICO': 'VILA GALE ATLANTICO',
            'VILLAS D´AGUA': 'VILLAS D´AGUA'
        }
        
        # Buscar todos os comissionistas
        cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
        commissioners = {row[1].upper(): row[0] for row in cursor.fetchall()}
        
        print(f"📋 Comissionistas na base de dados: {len(commissioners)}")
        print(f"🗺️  Mapeamento de hotéis: {len(hotel_mapping)}")
        
        # Analisar todos os arquivos Excel
        import glob
        excel_files = sorted(glob.glob("/Users/filipepacheco/CascadeProjects/carscraping/2025/CM-*.xlsx"))
        
        total_reservas = 0
        total_importadas = 0
        total_ignoradas = 0
        problematicas = []
        
        print(f"\n📁 Analisando {len(excel_files)} arquivos...")
        
        for file_path in excel_files:
            filename = file_path.split('/')[-1]
            print(f"\n📄 {filename}:")
            
            df = pd.read_excel(file_path)
            current_hotel = None
            reservas_arquivo = 0
            importadas_arquivo = 0
            ignoradas_arquivo = 0
            
            for idx, row in df.iterrows():
                # Identificar nome do hotel
                if pd.notna(row['Voucher']) and pd.isna(row['Data Entrega']):
                    current_hotel = row['Voucher'].strip().upper()
                    continue
                
                # Processar reserva
                if pd.notna(row['Data Entrega']) and current_hotel:
                    reservas_arquivo += 1
                    total_reservas += 1
                    
                    # Verificar se tem matching
                    commissioner_id = None
                    if current_hotel in hotel_mapping:
                        commissioner_name = hotel_mapping[current_hotel]
                        commissioner_id = commissioners.get(commissioner_name.upper())
                    
                    if commissioner_id:
                        importadas_arquivo += 1
                        total_importadas += 1
                    else:
                        ignoradas_arquivo += 1
                        total_ignoradas += 1
                        
                        # Guardar informações da reserva problemática
                        pickup_date = pd.to_datetime(row['Data Entrega'])
                        days = int(row['Dias']) if pd.notna(row['Dias']) else 1
                        loyalty_card_str = str(row['Loyalty Card']).replace(',', '.')
                        try:
                            loyalty_card_amount = float(loyalty_card_str)
                        except:
                            loyalty_card_amount = 0
                        
                        problematicas.append({
                            'arquivo': filename,
                            'hotel': current_hotel,
                            'data': pickup_date.strftime('%d/%m/%Y'),
                            'dias': days,
                            'valor': loyalty_card_amount
                        })
            
            print(f"  - Total reservas: {reservas_arquivo}")
            print(f"  - Importadas: {importadas_arquivo}")
            print(f"  - Ignoradas: {ignoradas_arquivo}")
        
        # Resumo final
        print(f"\n" + "=" * 80)
        print("RESUMO FINAL:")
        print("=" * 80)
        print(f"📊 Total de reservas encontradas: {total_reservas}")
        print(f"✅ Total importadas: {total_importadas}")
        print(f"❌ Total ignoradas: {total_ignoradas}")
        print(f"📈 Taxa de sucesso: {(total_importadas/total_reservas*100):.1f}%")
        
        # Mostrar detalhes das ignoradas
        if problematicas:
            print(f"\n❌ Detalhes das reservas ignoradas:")
            for i, prob in enumerate(problematicas[:10], 1):  # Mostrar só as 10 primeiras
                print(f"  {i}. [{prob['arquivo']}] {prob['hotel']}")
                print(f"     Data: {prob['data']} - {prob['dias']} dias - €{prob['valor']:.2f}")
            
            if len(problematicas) > 10:
                print(f"  ... e mais {len(problematicas) - 10} reservas ignoradas")
        else:
            print(f"\n✅ Nenhuma reserva foi ignorada!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    check_skipped_reservations()
