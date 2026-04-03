#!/usr/bin/env python3
"""
Script para encontrar matchings de brokers na base de dados
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

def find_broker_matches():
    """Procurar matchings de brokers"""
    print("=" * 80)
    print("PROCURA DE MATCHINGS DE BROKERS")
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
        
        # Buscar todos os comissionistas
        cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
        all_commissioners = cursor.fetchall()
        
        print(f"\n📋 Total de comissionistas na base de dados: {len(all_commissioners)}")
        
        # Identificar brokers pelo nome
        all_brokers = [(cid, name) for cid, name in all_commissioners if any(broker_word in name.upper() for broker_word in ['ABBYCAR', 'AQUAMAR', 'CARJET', 'DISCOVERCARS', 'CARALLIANCE', 'VIP'])]
        
        print(f"📋 Total de brokers identificados: {len(all_brokers)}")
        
        # Brokers encontrados nos ficheiros CM-26
        brokers_from_files = [
            'ABBYCAR-POA',
            'ABBYCAR-PREPAID', 
            'AQUAMAR',
            'CARJET-PREPAID',
            'DISCOVERCARS-PREPAID',
            'CARALLIANCE-POA',
            'CARALLIANCE-PREPAID',
            'VIP CARS-POA'
        ]
        
        print(f"\n🔍 Procurando matchings para {len(brokers_from_files)} brokers...")
        
        found_matches = {}
        still_missing = []
        
        for broker in brokers_from_files:
            broker_upper = broker.upper()
            matches = []
            
            # Procurar matchings exatos ou parciais
            for broker_id, broker_name in all_brokers:
                broker_name_upper = broker_name.upper()
                
                # Matching exato
                if broker_upper == broker_name_upper:
                    matches.append((broker_id, broker_name, "EXATO"))
                # Matching parcial - broker contém nome
                elif broker_upper in broker_name_upper:
                    matches.append((broker_id, broker_name, "BROKER EM NOME"))
                # Matching parcial - nome contém broker
                elif broker_name_upper in broker_upper:
                    matches.append((broker_id, broker_name, "NOME EM BROKER"))
                # Matching por palavras chave
                elif any(word in broker_name_upper for word in broker_upper.split() if len(word) > 2):
                    matches.append((broker_id, broker_name, "PALAVRA CHAVE"))
            
            if matches:
                found_matches[broker] = matches
            else:
                still_missing.append(broker)
        
        # Mostrar resultados
        print(f"\n✅ Matchings encontrados: {len(found_matches)}")
        print(f"❌ Ainda não encontrados: {len(still_missing)}")
        
        if found_matches:
            print(f"\n📋 Matchings encontrados:")
            for broker, matches in found_matches.items():
                print(f"\n🏢 {broker}:")
                for broker_id, broker_name, match_type in matches:
                    print(f"  - {broker_name} (ID: {broker_id}) [{match_type}]")
        
        if still_missing:
            print(f"\n❌ Brokers ainda sem matching:")
            for broker in sorted(still_missing):
                print(f"  - {broker}")
        
        # Mostrar todos os brokers para referência
        print(f"\n📋 Todos os brokers na base de dados:")
        for broker_id, broker_name in all_brokers:
            print(f"  ID: {broker_id} - {broker_name}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    find_broker_matches()
