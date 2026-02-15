#!/usr/bin/env python3
"""
Teste visual do método direto POST via requests (sem Selenium).
Faz a pesquisa CarJet usando scrape_carjet_requests e mostra os resultados.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from carjet_requests import scrape_carjet_requests

def main():
    # Datas: amanhã + 3 dias
    start = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
    end = start + timedelta(days=3)
    
    print("=" * 70)
    print(f"TESTE: scrape_carjet_requests (POST direto, sem Selenium)")
    print(f"Location: Faro")
    print(f"Datas: {start.strftime('%d/%m/%Y %H:%M')} → {end.strftime('%d/%m/%Y %H:%M')}")
    print("=" * 70)
    
    cars = scrape_carjet_requests("faro", start, end)
    
    print("\n" + "=" * 70)
    print(f"RESULTADO: {len(cars)} carros encontrados")
    print("=" * 70)
    
    if not cars:
        print("❌ Nenhum carro encontrado - método requests pode estar bloqueado")
        return
    
    # Agrupar por supplier
    suppliers = {}
    for car in cars:
        sup = car.get('supplier', 'Unknown')
        if sup not in suppliers:
            suppliers[sup] = []
        suppliers[sup].append(car)
    
    print(f"\n📊 {len(suppliers)} fornecedores:")
    for sup, sup_cars in sorted(suppliers.items()):
        print(f"  {sup}: {len(sup_cars)} carros")
    
    # Mostrar primeiros 20 carros
    print(f"\n🚗 Primeiros 20 carros:")
    for i, car in enumerate(cars[:20]):
        name = car.get('car') or car.get('car_name', '?')
        sup = car.get('supplier', '?')
        price = car.get('price', '?')
        print(f"  {i+1:3d}. {name:<35s} | {sup:<20s} | {price}")
    
    if len(cars) > 20:
        print(f"  ... e mais {len(cars) - 20} carros")

if __name__ == '__main__':
    main()
