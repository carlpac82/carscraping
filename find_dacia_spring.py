#!/usr/bin/env python3
"""
Script para procurar Dacia Spring na base de dados e ver como está classificado
"""

import json
import os

def find_dacia_spring():
    """Procurar Dacia Spring em todos os ficheiros JSON de resultados"""
    
    print("=" * 80)
    print("PROCURANDO: Dacia Spring")
    print("=" * 80)
    
    # Procurar no diretório atual
    for filename in os.listdir('.'):
        if filename.endswith('.json') and 'result' in filename.lower():
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Procurar em diferentes estruturas possíveis
                    items = []
                    if isinstance(data, list):
                        items = data
                    elif isinstance(data, dict):
                        if 'items' in data:
                            items = data['items']
                        elif 'days' in data:
                            for day_data in data['days'].values():
                                if isinstance(day_data, list):
                                    items.extend(day_data)
                                elif isinstance(day_data, dict) and 'items' in day_data:
                                    items.extend(day_data['items'])
                    
                    # Procurar Dacia Spring
                    for item in items:
                        car_name = item.get('car', '').lower()
                        if 'dacia' in car_name and 'spring' in car_name:
                            print(f"\n✅ ENCONTRADO em: {filename}")
                            print(f"   Nome: {item.get('car', 'N/A')}")
                            print(f"   Grupo: {item.get('group', 'N/A')}")
                            print(f"   Categoria: {item.get('category', 'N/A')}")
                            print(f"   Transmissão: {item.get('transmission', 'N/A')}")
                            print(f"   Supplier: {item.get('supplier', 'N/A')}")
                            print(f"   Preço: {item.get('price', 'N/A')}")
                            
            except Exception as e:
                pass
    
    print("\n" + "=" * 80)
    print("Procura concluída")
    print("=" * 80)

if __name__ == "__main__":
    find_dacia_spring()
