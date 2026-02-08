#!/usr/bin/env python3
"""
Debug: ver como filterAgrupVeh funciona no CarJet
Extrair o JavaScript e entender o mecanismo de filtragem
"""
import requests
import re
import time

SESSION_URL = "https://www.carjet.com/do/list/pt?s=ab62cb74-e360-4119-8236-dc822802cb23&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-PT,pt;q=0.9',
})

print("📌 Obtendo página principal...")
resp = session.get(SESSION_URL, timeout=15)
html = resp.text
print(f"   HTML: {len(html)} bytes")

# 1. Procurar definição de filterAgrupVeh
print("\n🔍 Procurando filterAgrupVeh no JavaScript...")
matches = re.findall(r'function\s+filterAgrupVeh[^{]*\{[^}]*\}', html, re.DOTALL)
if matches:
    for m in matches:
        print(f"   ENCONTRADO: {m[:500]}")
else:
    # Procurar de forma mais ampla
    idx = html.find('filterAgrupVeh')
    if idx >= 0:
        context = html[max(0, idx-200):idx+500]
        print(f"   Contexto (±500 chars):")
        print(f"   {context}")
    else:
        print("   NÃO encontrado no HTML principal")

# 2. Procurar scripts externos
print("\n🔍 Procurando scripts externos...")
scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html)
for s in scripts:
    print(f"   {s}")

# 3. Procurar formulário de filtro
print("\n🔍 Procurando formulários de filtro...")
forms = re.findall(r'<form[^>]*id=["\']([^"\']*)["\'][^>]*>', html)
for f in forms:
    print(f"   Form: {f}")

# 4. Procurar frmAgrp no HTML
print("\n🔍 Procurando frmAgrp no HTML...")
agrp_matches = re.findall(r'frmAgrp[^"\'<>]{0,200}', html)
for m in agrp_matches[:5]:
    print(f"   {m[:200]}")

# 5. Procurar data-agrp ou categorias no HTML
print("\n🔍 Procurando categorias/agrupamentos no HTML...")
cat_matches = re.findall(r'(data-agrp|data-agrup|agrup|VANS|MINI|COMP|FAMI)[^"\'<>]{0,100}', html)
for m in cat_matches[:20]:
    print(f"   {m[:150]}")

# 6. Verificar se há artigos com data-agrp
print("\n🔍 Procurando artigos com atributos de categoria...")
article_attrs = re.findall(r'<article[^>]{0,500}>', html)
if article_attrs:
    print(f"   {len(article_attrs)} artigos encontrados")
    for a in article_attrs[:3]:
        print(f"   {a[:300]}")
else:
    print("   Nenhum artigo encontrado")

# 7. Contar carros no HTML principal (sem filtro)
print("\n🔍 Contando carros no HTML principal...")
car_cards = re.findall(r'class="carCardWeb"', html)
car_cards_mob = re.findall(r'class="carCardMob"', html)
print(f"   carCardWeb: {len(car_cards)}")
print(f"   carCardMob: {len(car_cards_mob)}")

# 8. Procurar Jogger no HTML
print("\n🔍 Procurando 'Jogger' no HTML principal...")
jogger_idx = html.lower().find('jogger')
if jogger_idx >= 0:
    print(f"   ENCONTRADO em posição {jogger_idx}")
    print(f"   Contexto: {html[max(0,jogger_idx-100):jogger_idx+200]}")
else:
    print("   NÃO encontrado no HTML principal")

# 9. Procurar Dacia no HTML
print("\n🔍 Procurando 'Dacia' no HTML principal...")
dacia_count = html.lower().count('dacia')
print(f"   'Dacia' aparece {dacia_count} vezes")
if dacia_count > 0:
    for m in re.finditer(r'[Dd]acia\s+\w+', html):
        print(f"   → {m.group()}")
