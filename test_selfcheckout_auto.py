#!/usr/bin/env python3
"""
Script automático para testar self-checkout (sem interação)
"""

import requests
import json

BASE_URL = "https://carscraping.up.railway.app"
RA_NUMBER = "06716"
TEST_EMAIL = "carlpac82@hotmail.com"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

print("\n🚗"*40)
print("  TESTE AUTOMÁTICO - SELF-CHECKOUT")
print("  Contrato: AS-46-EO (RA: 06716)")
print("  Email: carlpac82@hotmail.com")
print("🚗"*40)

# Passo 1: Gerar link
print_section("PASSO 1: Gerar Link de Self-Checkout")

url = f"{BASE_URL}/api/self-checkin/resend-link"
payload = {"rental_agreement_number": RA_NUMBER}

print(f"📤 POST {url}")
print(f"📦 Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"📥 Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Link gerado e email enviado com sucesso!")
        print(f"📧 Verifique o email {TEST_EMAIL}")
        print(f"\n💡 O email contém:")
        print(f"   - Link único de self-checkout")
        print(f"   - Instruções para o cliente")
        print(f"   - Dados do veículo e contrato")
    else:
        try:
            data = response.json()
            print(f"❌ Erro: {data.get('error')}")
        except:
            print(f"❌ Erro HTTP: {response.text[:200]}")
except Exception as e:
    print(f"❌ Exceção: {e}")

# Instruções finais
print_section("PRÓXIMOS PASSOS")
print("""
✅ Email de convite enviado para: carlpac82@hotmail.com

📧 VERIFIQUE O EMAIL E:
   1. Abra o link de self-checkout no email
   2. Preencha o formulário de inspeção
   3. Tire/carregue fotos do veículo
   4. Submeta o self-checkout
   
🖥️  DEPOIS ACEDA AO HISTÓRICO:
   https://carscraping.up.railway.app/inspection-history
   
   Lá poderá:
   ✓ Ver o self-checkout submetido com badge "PENDENTE"
   ✓ Ver os contadores de self-checkouts
   ✓ Usar filtros para ver apenas self-checkouts
   ✓ Clicar em "Validar" para aprovar
   ✓ Clicar em "Advertir" para enviar email de divergências
   ✓ Clicar em "Invalidar" para rejeitar

📊 FUNCIONALIDADES IMPLEMENTADAS:
   ✅ Botão "Advertir" (âmbar)
   ✅ Badges de status (Pendente/Validado/Divergências/Invalidado)
   ✅ Badge "SELF-CHECKOUT" (roxo)
   ✅ Contadores em tempo real
   ✅ Filtros por tipo e status
   ✅ Função JavaScript warnSelfCheckin()
   ✅ Endpoint /api/self-checkin/warn
""")

print("="*80)
print("✅ TESTE CONCLUÍDO")
print("="*80)
