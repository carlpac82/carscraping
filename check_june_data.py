#!/usr/bin/env python3
"""
Script para diagnosticar dados de junho no histórico
"""
import psycopg2
import json
import os
from datetime import datetime

def check_june_searches():
    try:
        # Connect to PostgreSQL database
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL não encontrada nas variáveis de ambiente")
            return
            
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Find all June searches (2026-06)
        cursor.execute("""
            SELECT id, location, search_type, search_date, month_key, 
                   price_count, dias, prices_data, supplier_data
            FROM automated_search_history
            WHERE month_key LIKE '%-06'
            ORDER BY search_date DESC
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("❌ Nenhuma pesquisa de junho encontrada na base de dados")
            return
        
        print(f"✅ Encontradas {len(rows)} pesquisas de junho\n")
        
        for row in rows:
            row_id, location, search_type, search_date, month_key, price_count, dias, prices_data, supplier_data = row
            
            print(f"{'='*80}")
            print(f"ID: {row_id}")
            print(f"Location: {location}")
            print(f"Search Type: {search_type}")
            print(f"Date: {search_date}")
            print(f"Month: {month_key}")
            print(f"Price Count: {price_count}")
            
            # Parse dias
            try:
                dias_parsed = json.loads(dias) if dias else []
                print(f"Dias: {dias_parsed}")
            except:
                print(f"⚠️ Erro ao fazer parse dos dias")
            
            # Parse prices_data
            try:
                prices_parsed = json.loads(prices_data) if prices_data else {}
                print(f"Grupos com preços: {list(prices_parsed.keys())}")
                print(f"Total de grupos: {len(prices_parsed)}")
            except:
                print(f"⚠️ Erro ao fazer parse dos prices_data")
            
            # Parse supplier_data (PostgreSQL já retorna como dict)
            try:
                if isinstance(supplier_data, dict):
                    supplier_parsed = supplier_data
                elif isinstance(supplier_data, str):
                    supplier_parsed = json.loads(supplier_data)
                else:
                    supplier_parsed = {}
                
                if not supplier_parsed:
                    print(f"❌ PROBLEMA: supplier_data está VAZIO!")
                else:
                    print(f"✅ supplier_data existe")
                    print(f"   Keys: {list(supplier_parsed.keys())[:10]}")
                    print(f"   Total keys: {len(supplier_parsed)}")
                    
                    # Check format
                    first_key = list(supplier_parsed.keys())[0] if supplier_parsed else None
                    if first_key:
                        first_value = supplier_parsed[first_key]
                        if isinstance(first_value, list):
                            print(f"   Formato: DAY→CARS ✅")
                            print(f"   Exemplo dia {first_key}: {len(first_value)} carros")
                            if first_value:
                                print(f"   Primeiro carro: {first_value[0]}")
                        elif isinstance(first_value, dict):
                            print(f"   Formato: GROUP→DAY→CARS")
                            print(f"   Exemplo grupo {first_key}: {list(first_value.keys())}")
                            # Mostrar estrutura de um carro
                            first_day = list(first_value.keys())[0] if first_value else None
                            if first_day:
                                cars_in_day = first_value[first_day]
                                if cars_in_day and len(cars_in_day) > 0:
                                    print(f"   Exemplo carro no dia {first_day}:")
                                    print(f"      {json.dumps(cars_in_day[0], indent=6)}")
                        else:
                            print(f"   Formato desconhecido: {type(first_value)}")
                            
            except Exception as e:
                print(f"⚠️ Erro ao fazer parse do supplier_data: {e}")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_june_searches()
