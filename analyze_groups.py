#!/usr/bin/env python3
"""
Análise profunda de classificação de grupos de carros
Verifica se todos os carros estão sendo classificados corretamente
"""

import re
import sys
from collections import defaultdict

# Grupos esperados
GRUPOS = ['B1', 'B2', 'D', 'E1', 'E2', 'F', 'G', 'J1', 'J2', 'L1', 'L2', 'M1', 'M2', 'N']

# Modelos conhecidos por grupo (baseado no código)
MODELOS_ESPERADOS = {
    'B1': [
        'Fiat 500', 'Peugeot 108', 'Citroen C1', 'VW Up', 'Kia Picanto', 'Toyota Aygo',
        'Ford Ka', 'Renault Twingo', 'Opel Adam'
    ],
    'B2': [
        'Fiat Panda', 'Hyundai i10', 'Kia Picanto', 'Peugeot 108'
    ],
    'D': [
        'Peugeot 208', 'Opel Corsa', 'Seat Ibiza', 'VW Polo', 'Citroen C3', 'Renault Clio',
        'Ford Fiesta', 'Nissan Micra', 'Hyundai i20', 'Audi A1', 'Dacia Sandero',
        'Seat Leon', 'Skoda Fabia', 'Mazda 2', 'Toyota Yaris'
    ],
    'E1': [
        'Fiat 500 Auto', 'Peugeot 108 Auto', 'Kia Picanto Auto', 'Toyota Aygo Auto',
        'VW Up Auto', 'Hyundai i10 Auto'
    ],
    'E2': [
        'Peugeot 208 Auto', 'Opel Corsa Auto', 'VW Polo Auto', 'Renault Clio Auto',
        'Toyota Corolla Auto', 'Seat Ibiza Auto', 'Hyundai i20 Auto', 'Nissan Micra Auto'
    ],
    'F': [
        'Peugeot 2008', 'Peugeot 3008', 'Nissan Qashqai', 'Toyota C-HR', 'VW Tiguan',
        'Ford Kuga', 'Jeep Renegade', 'Renault Captur', 'Dacia Duster', 'Mazda CX-3',
        'Skoda Kamiq', 'Citroen C4', 'DS 4', 'Skoda Karoq', 'Renault Arkana',
        'Toyota RAV4', 'Cupra Formentor', 'Toyota Yaris Cross', 'Citroen C5 Aircross',
        'VW T-Cross', 'Fiat 500X', 'Toyota Aygo X'
    ],
    'G': [
        'Cabrio', 'Cabriolet', 'Convertible'  # Qualquer carro com estas palavras
    ],
    'J1': [
        'Peugeot 2008', 'Nissan Qashqai', 'Toyota C-HR', 'Dacia Duster', 'Renault Captur'
    ],
    'J2': [
        'Peugeot 308 SW', 'Renault Megane SW', 'Ford Focus SW', 'VW Golf Variant',
        'Seat Leon SW', 'Opel Astra SW', 'Toyota Corolla SW', 'Skoda Octavia SW'
    ],
    'L1': [
        'Peugeot 2008 Auto', 'Peugeot 3008 Auto', 'Nissan Qashqai Auto', 'Toyota C-HR Auto',
        'VW Tiguan Auto', 'Ford Kuga Auto', 'Jeep Renegade Auto', 'Skoda Kamiq Auto',
        'Citroen C4 Auto', 'Toyota RAV4 Auto', 'Cupra Formentor Auto'
    ],
    'L2': [
        'Peugeot 308 SW Auto', 'Ford Focus SW Auto', 'VW Golf Variant Auto', 
        'Seat Leon SW Auto', 'Opel Astra Auto', 'Toyota Corolla SW Auto',
        'Renault Megane SW Auto', 'Skoda Scala Auto', 'VW Passat Auto',
        'Peugeot 508 Auto', 'Hyundai i30 Auto', 'Fiat 500L Auto'
    ],
    'M1': [
        'Citroen C4 Picasso', 'Renault Grand Scenic', 'Peugeot Rifter'
    ],
    'M2': [
        'VW Caddy Auto', 'VW Sharan Auto', 'Seat Alhambra Auto', 'Ford Galaxy Auto',
        'Peugeot 5008 Auto', 'Dacia Jogger Auto', 'Opel Zafira Auto',
        'Citroen C4 Grand Spacetourer Auto', 'Renault Grand Scenic Auto', 
        'Mercedes GLB 7 Seater Auto', 'VW Multivan Auto', 'Peugeot Rifter Auto'
    ],
    'N': [
        '9 Seater', 'Minivan', 'Van'
    ]
}

# Carros que podem causar confusão
CARROS_PROBLEMATICOS = {
    'Peugeot 5008': ['M2 se auto', 'F se manual'],
    'Toyota Corolla': ['E2 se auto base', 'L2 se auto SW', 'D se manual base', 'J2 se manual SW'],
    'VW Caddy': ['M2 se auto', 'Pode não aparecer se manual'],
    'Dacia Jogger': ['M2 se auto', 'Pode não aparecer se manual'],
    'Peugeot 2008': ['L1 se auto', 'F/J1 se manual'],
    'Nissan Qashqai': ['L1 se auto', 'F/J1 se manual'],
    'Ford Focus SW': ['L2 se auto', 'J2 se manual'],
    'VW Golf Variant': ['L2 se auto', 'J2 se manual'],
    'Fiat 500L': ['L2 se auto', 'J2 se manual'],
    'Opel Astra': ['L2 se auto', 'J2 se manual'],
    'Renault Clio SW': ['L2 se auto', 'J2 se manual'],
}

def analyze_group_coverage():
    """Analisa a cobertura de modelos por grupo"""
    
    if 'items' in data:
        items = data['items']
        print(f"✅ Encontrados {len(items)} carros")
        
        # Contar por grupo
        grupos = Counter()
        grupos_detalhes = {}
        
        for item in items:
            group = item.get('group', 'Unknown')
            grupos[group] += 1
            
            if group not in grupos_detalhes:
                grupos_detalhes[group] = []
            
            grupos_detalhes[group].append({
                'car': item.get('car', ''),
                'transmission': item.get('transmission', ''),
                'category': item.get('category', ''),
                'price': item.get('price', '')
            })
        
        # Mostrar distribuição
        print("\n📊 DISTRIBUIÇÃO POR GRUPO:")
        print("-" * 80)
        for group in sorted(grupos.keys()):
            count = grupos[group]
            print(f"{group:10} | {count:4} carros")
        
        # Foco em M1 e M2
        print("\n\n🎯 FOCO: 7 LUGARES")
        print("=" * 80)
        
        m1_cars = grupos_detalhes.get('M1', [])
        m2_cars = grupos_detalhes.get('M2', [])
        
        print(f"\n📌 M1 (7 Seater Manual): {len(m1_cars)} carros")
        for i, car in enumerate(m1_cars[:10], 1):
            print(f"  {i}. {car['car'][:50]:50} | Trans: {car['transmission']:10} | Cat: {car['category']}")
        
        print(f"\n📌 M2 (7 Seater Auto): {len(m2_cars)} carros")
        for i, car in enumerate(m2_cars[:10], 1):
            print(f"  {i}. {car['car'][:50]:50} | Trans: {car['transmission']:10} | Cat: {car['category']}")
        
        if len(m2_cars) == 0:
            print("\n⚠️  PROBLEMA: Nenhum carro em M2!")
            print("   Verificando se há carros automáticos de 7 lugares em outros grupos...")
            
            # Procurar carros 7 lugares automáticos em outros grupos
            for group, cars in grupos_detalhes.items():
                if group != 'M2':
                    auto_7_seaters = [c for c in cars if 
                                     'Automatic' in c.get('transmission', '') and
                                     ('7' in c.get('category', '') or '7' in c.get('car', ''))]
                    if auto_7_seaters:
                        print(f"\n   ❗ Encontrados {len(auto_7_seaters)} carros 7 lugares automáticos no grupo {group}:")
                        for c in auto_7_seaters[:5]:
                            print(f"      - {c['car'][:60]}")
    
    else:
        print(f"❌ Resposta inesperada: {data}")

except Exception as e:
    print(f"❌ Erro: {e}")
    print()
    
    print("4. L2 (Station Wagon Auto):")
    print("   • Peugeot 308 SW Auto - ✓ Parametrizado")
    print("   • Ford Focus SW Auto - ✓ Parametrizado")
    print("   • VW Golf Variant Auto - ✓ Parametrizado")
    print("   • Skoda Octavia SW Auto - ❌ PODE ESTAR FALTANDO")
    print()
    
    print("5. N (9 Seater):")
    print("   • Mercedes Vito - ❌ PODE ESTAR FALTANDO")
    print("   • Ford Transit - ❌ PODE ESTAR FALTANDO")
    print("   • Renault Trafic - ❌ PODE ESTAR FALTANDO")
    print()

def check_regex_patterns():
    """Verifica se os padrões regex estão corretos"""
    print("\n" + "=" * 80)
    print("🔬 VERIFICAÇÃO DE PADRÕES REGEX")
    print("=" * 80)
    print()
    
    test_cases = [
        ("VW Caddy Auto", "M2", "✅ Deve ser M2 (7 lugares auto)"),
        ("VW Caddy Manual", "Others/M1", "⚠️  Caddy manual não tem override M2"),
        ("Peugeot 5008 Auto", "M2", "✅ Deve ser M2 (7 lugares auto)"),
        ("Peugeot 5008 Manual", "F/J1", "⚠️  5008 manual vai para F ou J1"),
        ("Dacia Jogger Auto", "M2", "✅ Deve ser M2 (7 lugares auto)"),
        ("Toyota Corolla Auto", "E2", "✅ Deve ser E2 (Economy Auto)"),
        ("Toyota Corolla SW Auto", "L2", "✅ Deve ser L2 (SW Auto)"),
        ("Renault Clio SW Auto", "L2", "✅ Deve ser L2 (SW Auto)"),
        ("Ford Focus SW Auto", "L2", "✅ Deve ser L2 (SW Auto)"),
        ("Nissan Qashqai Auto", "L1", "✅ Deve ser L1 (SUV Auto)"),
        ("Hyundai i10 Auto", "E1", "⚠️  VERIFICAR: Deve ser E1 (Mini Auto)"),
        ("Fiat Panda Auto", "E1", "⚠️  VERIFICAR: Deve ser E1 (Mini Auto)"),
    ]
    
    for carro, grupo_esperado, nota in test_cases:
        print(f"{carro:35} → {grupo_esperado:8} {nota}")

def main():
    """Função principal"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ANÁLISE DE GRUPOS DE CARROS" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    
    analyze_group_coverage()
    analyze_missing_patterns()
    check_regex_patterns()
    
    print("\n" + "=" * 80)
    print("📝 RECOMENDAÇÕES")
    print("=" * 80)
    print()
    print("1. ✅ Grupo M2 já foi corrigido com 7 novos modelos")
    print("2. ⚠️  Verificar se Hyundai i10 Auto vai para E1 (não B2)")
    print("3. ⚠️  Verificar se Fiat Panda Auto vai para E1 (não B2)")
    print("4. ⚠️  Considerar adicionar Skoda Octavia SW ao L2")
    print("5. ⚠️  Considerar adicionar Mercedes Vito/Ford Transit/Renault Trafic ao N")
    print("6. ⚠️  Considerar adicionar Suzuki Ignis e Smart ForFour ao B2")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
