#!/usr/bin/env python3
"""
Script para testar porque Dacia Spring está a ser classificado como M2 e N
"""

import sys
import re

def test_dacia_spring():
    """Testar vários nomes possíveis do Dacia Spring"""
    
    test_cases = [
        ("Dacia Spring Electric Aut.", "Economy Automatic", "Automatic"),
        ("Dacia Spring Electric", "Economy Automatic", "Automatic"),
        ("Dacia Spring", "Economy Automatic", "Automatic"),
        ("Dacia Spring Aut.", "Economy", "Automatic"),
        ("Dacia Spring Auto", "Economy", "Automatic"),
    ]
    
    # Copiar padrões do main.py
    seven_seater_patterns = [
        r'\bpeugeot\s*5008\b',
        r'\bcitro[eë]n\s*c4\s*picasso\b',
        r'\brenault\s*(grand\s*)?scenic\b',
        r'\b(vw|volkswagen)\s*caddy\b',
        r'\bdacia\s*lodgy\b',
        r'\bdacia\s*jogger\b',
    ]
    
    nine_seater_patterns = [
        r'\bford\s*transit\b',
        r'\bmercedes\s*(benz\s*)?vito\b',
        r'\bopel\s*vivaro\b',
        r'\brenault\s*trafic\b',
    ]
    
    print("=" * 80)
    print("TESTE: Dacia Spring Electric")
    print("=" * 80)
    
    for car_name, category, transmission in test_cases:
        car_lower = car_name.lower()
        
        print(f"\n🚗 Testando: '{car_name}'")
        print(f"   Categoria: {category}")
        print(f"   Transmissão: {transmission}")
        
        # Testar 7 lugares
        matched_7 = False
        for pattern in seven_seater_patterns:
            if re.search(pattern, car_lower, re.IGNORECASE):
                print(f"   ❌ MATCH 7 LUGARES: {pattern}")
                matched_7 = True
                break
        
        if not matched_7:
            print(f"   ✅ NÃO faz match com 7 lugares")
        
        # Testar 9 lugares
        matched_9 = False
        for pattern in nine_seater_patterns:
            if re.search(pattern, car_lower, re.IGNORECASE):
                print(f"   ❌ MATCH 9 LUGARES: {pattern}")
                matched_9 = True
                break
        
        if not matched_9:
            print(f"   ✅ NÃO faz match com 9 lugares")
        
        # Verificar se tem "dacia" no nome
        if 'dacia' in car_lower:
            print(f"   ℹ️  Contém 'dacia' - verificar padrões Dacia:")
            for pattern in seven_seater_patterns:
                if 'dacia' in pattern:
                    print(f"      - Padrão Dacia 7 lugares: {pattern}")
                    if re.search(pattern, car_lower, re.IGNORECASE):
                        print(f"        ❌ MATCH!")
                    else:
                        print(f"        ✅ NO MATCH")

if __name__ == "__main__":
    test_dacia_spring()
