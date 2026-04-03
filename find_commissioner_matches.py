#!/usr/bin/env python3
"""
Script para encontrar matchings de comissionistas na base de dados
"""
import os
import psycopg2
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

def find_commissioner_matches():
    """Procurar matchings de comissionistas"""
    print("=" * 80)
    print("PROCURA DE MATCHINGS DE COMISSIONISTAS")
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
        
        # Buscar todos os comissionistas
        cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
        all_commissioners = cursor.fetchall()
        
        print(f"\n📋 Total de comissionistas na base de dados: {len(all_commissioners)}")
        
        # Hotéis não mapeados que precisamos de encontrar
        unmapped_hotels = [
            'ALBUFEIRA SOL',
            'APARTAMENTOS CABRITA', 
            'AREIAS VILLAGE',
            'HOTEL BOAVISTA',
            'HOTEL JUPITER', 
            'HOTEL CALIFORNIA',
            'PORTO BAY BLUE OCEAN',
            'PORTO BAY FALESIA',
            'VILA GALE PRAIA',
            'VILAS SÃO VICENTE',
            'ALFAGAR',
            'ALGARVE & COMPANHIA',
            'ALGAVE MOTORHOME PARK',
            'ALTO DA COLINA',
            'AQUA PEDRA DOS BICOS',
            'AQUAMAR',
            'BELA VISTA JARDIM II',
            'BORDA D´AGUA',
            'BROKERS - DIRECTOS',
            'CLUB MED- EMMA',
            'CLUBE ALBUFEIRA',
            'CLUBE MED - MANUELA',
            'JARDINS DE VALE DE PARRA',
            'JOAO FERREIRA',
            'KR HOTELS',
            'NAU SAO RAFAEL SUITES',
            'NOVO CHORO',
            'OCEAN VIEW',
            'PINHEIROS DA BALAIA',
            'QUINTA PEDRA DOS BICOS',
            'REAL SANTA EULALIA',
            'REGENCY SALGADOS',
            'SEM COMISSÃO',
            'SUNCHINE RESTAURANTE',
            'TTO OLHOS DE AGUA',
            'VALE CARRO',
            'VICTORIA',
            'VILA GALE ATLANTICO',
            'VILLAS D´AGUA'
        ]
        
        print(f"\n🔍 Procurando matchings para {len(unmapped_hotels)} hotéis...")
        
        found_matches = {}
        still_missing = []
        
        for hotel in unmapped_hotels:
            hotel_upper = hotel.upper()
            matches = []
            
            # Procurar matchings exatos ou parciais
            for comm_id, comm_name in all_commissioners:
                comm_name_upper = comm_name.upper()
                
                # Matching exato
                if hotel_upper == comm_name_upper:
                    matches.append((comm_id, comm_name, "EXATO"))
                # Matching parcial - hotel contém nome do comissionista
                elif hotel_upper in comm_name_upper:
                    matches.append((comm_id, comm_name, "HOTEL EM COMISSIONISTA"))
                # Matching parcial - comissionista contém nome do hotel
                elif comm_name_upper in hotel_upper:
                    matches.append((comm_id, comm_name, "COMISSIONISTA EM HOTEL"))
                # Matching por palavras chave
                elif any(word in comm_name_upper for word in hotel_upper.split() if len(word) > 2):
                    matches.append((comm_id, comm_name, "PALAVRA CHAVE"))
            
            if matches:
                found_matches[hotel] = matches
            else:
                still_missing.append(hotel)
        
        # Mostrar resultados
        print(f"\n✅ Matchings encontrados: {len(found_matches)}")
        print(f"❌ Ainda não encontrados: {len(still_missing)}")
        
        if found_matches:
            print(f"\n📋 Matchings encontrados:")
            for hotel, matches in found_matches.items():
                print(f"\n🏨 {hotel}:")
                for comm_id, comm_name, match_type in matches:
                    print(f"  - {comm_name} (ID: {comm_id}) [{match_type}]")
        
        if still_missing:
            print(f"\n❌ Hotéis ainda sem matching:")
            for hotel in sorted(still_missing):
                print(f"  - {hotel}")
        
        # Mostrar todos os comissionistas para referência
        print(f"\n📋 Todos os comissionistas na base de dados:")
        for comm_id, comm_name in all_commissioners:
            print(f"  ID: {comm_id} - {comm_name}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    find_commissioner_matches()
