#!/usr/bin/env python3
"""
Teste Visual da API - Abre Chrome e faz pesquisa
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração
API_URL = "http://localhost:8000/api/track-by-params"

# Dados de teste - Aeroporto de Faro, 5 dias, daqui a ~1 mês
today = datetime.now()
start_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

payload = {
    "location": "Aeroporto de Faro",
    "start_date": start_date,
    "start_time": "15:00",
    "days": 5,
    "end_date": "",
    "end_time": "15:00"
}

print("=" * 80)
print("TESTE VISUAL DA API - SCRAPING CARJET")
print("=" * 80)
print(f"\n📍 Location: {payload['location']}")
print(f"📅 Start Date: {payload['start_date']}")
print(f"⏰ Start Time: {payload['start_time']}")
print(f"📆 Days: {payload['days']}")
print(f"\n🔗 API URL: {API_URL}")
print(f"\n⏳ Enviando request...\n")

try:
    # Fazer request para a API
    response = requests.post(API_URL, json=payload, timeout=120)
    
    print(f"\n✅ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get("ok"):
            items = data.get("items", [])
            print(f"\n🎉 SUCESSO! {len(items)} carros encontrados!")
            
            # Mostrar primeiros 5 resultados
            print("\n" + "=" * 80)
            print("PRIMEIROS 5 RESULTADOS:")
            print("=" * 80)
            
            for i, item in enumerate(items[:5], 1):
                print(f"\n{i}. {item.get('name', 'N/A')}")
                print(f"   💰 Preço: €{item.get('price', 'N/A')}")
                print(f"   🏢 Supplier: {item.get('supplier', 'N/A')}")
                print(f"   🚗 Group: {item.get('group', 'N/A')}")
                print(f"   ⚙️  Transmission: {item.get('transmission', 'N/A')}")
        else:
            print(f"\n❌ ERRO: {data.get('error', 'Unknown error')}")
    else:
        print(f"\n❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("\n⏰ TIMEOUT! A API demorou mais de 120 segundos.")
except requests.exceptions.ConnectionError:
    print("\n❌ ERRO DE CONEXÃO! Certifica-te que o servidor está a correr.")
except Exception as e:
    print(f"\n❌ ERRO: {e}")

print("\n" + "=" * 80)
print("TESTE CONCLUÍDO")
print("=" * 80)
