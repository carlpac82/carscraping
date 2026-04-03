#!/usr/bin/env python3
"""
Script para encontrar matchings CORRETOS de brokers na base de dados
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

def find_correct_broker_matches():
    """Procurar matchings CORRETOS de brokers"""
    print("=" * 80)
    print("PROCURA DE MATCHINGS CORRETOS DE BROKERS")
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
        
        # Lista CORRETA de brokers (fornecida pelo user)
        correct_brokers = [
            'ABBYCAR-POA',
            'ABBYCAR-PREPAID',
            'AP',
            'API-WEB',
            'API',
            'BROKERS - DIRECTOS',
            'CARALLIANCE-POA',
            'CARALLIANCE-PREPAID',
            'CARJET-PREPAID',
            'CARJET',
            'DISCOVERCARS-PREPAID',
            'DISCOVERCARS-POA',
            'RENTALCARS',
            'VIP CARS-POA',
            'VIP CARS'
        ]
        
        print(f"\n🔍 Procurando matchings para {len(correct_brokers)} brokers CORRETOS...")
        
        found_matches = {}
        still_missing = []
        
        for broker in correct_brokers:
            broker_upper = broker.upper()
            matches = []
            
            # Procurar matchings exatos ou parciais
            for comm_id, comm_name in all_commissioners:
                comm_name_upper = comm_name.upper()
                
                # Matching exato
                if broker_upper == comm_name_upper:
                    matches.append((comm_id, comm_name, "EXATO"))
                # Matching parcial - broker contém nome
                elif broker_upper in comm_name_upper:
                    matches.append((comm_id, comm_name, "BROKER EM NOME"))
                # Matching parcial - nome contém broker
                elif comm_name_upper in broker_upper:
                    matches.append((comm_id, comm_name, "NOME EM BROKER"))
                # Matching por palavras chave
                elif any(word in comm_name_upper for word in broker_upper.split() if len(word) > 2):
                    matches.append((comm_id, comm_name, "PALAVRA CHAVE"))
            
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
                for comm_id, comm_name, match_type in matches:
                    print(f"  - {comm_name} (ID: {comm_id}) [{match_type}]")
        
        if still_missing:
            print(f"\n❌ Brokers ainda sem matching:")
            for broker in sorted(still_missing):
                print(f"  - {broker}")
        
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
    find_correct_broker_matches()
