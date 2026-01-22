#!/usr/bin/env python3
"""
Script para testar se o Railway já tem o código atualizado com clientName
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://rentalprices.pt"
USERNAME = os.getenv("ADMIN_USERNAME", "admin")
PASSWORD = os.getenv("ADMIN_PASSWORD")

def test_resend_and_check():
    """Reenviar link e verificar se o nome do cliente aparece"""
    
    # Login
    print("🔐 Fazendo login...")
    login_response = requests.post(
        f"{BASE_URL}/api/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.status_code}")
        return
    
    cookies = login_response.cookies
    print("✅ Login bem-sucedido\n")
    
    # Reenviar link para RA 06716
    print("📧 Reenviando link para RA 06716...")
    resend_response = requests.post(
        f"{BASE_URL}/api/self-checkin/resend-link",
        json={"rental_agreement_number": "06716"},
        cookies=cookies
    )
    
    if resend_response.status_code != 200:
        print(f"❌ Erro ao reenviar: {resend_response.status_code}")
        print(resend_response.text)
        return
    
    data = resend_response.json()
    print(f"✅ Link reenviado!")
    print(f"📧 Email: {data.get('email', 'N/A')}")
    
    token = data.get('token', '')
    if not token:
        print("❌ Token não retornado")
        return
    
    print(f"🔗 Token: {token[:30]}...\n")
    
    # Verificar dados do self-checkout
    print("🔍 Verificando dados do self-checkout...")
    checkout_response = requests.get(
        f"{BASE_URL}/api/self-checkout/{token}"
    )
    
    if checkout_response.status_code != 200:
        print(f"❌ Erro ao obter dados: {checkout_response.status_code}")
        print(checkout_response.text)
        return
    
    checkout_data = checkout_response.json()
    
    if not checkout_data.get('success'):
        print(f"❌ Erro: {checkout_data.get('error')}")
        return
    
    client_name = checkout_data.get('data', {}).get('client_name')
    
    print(f"✅ Dados obtidos com sucesso!")
    print(f"👤 Nome do cliente: {client_name}")
    
    if client_name and client_name != "Cliente":
        print(f"\n✅ SUCESSO! O nome do cliente está a ser extraído corretamente!")
        print(f"   Nome: {client_name}")
    else:
        print(f"\n❌ PROBLEMA! O nome do cliente ainda não está a ser extraído")
        print(f"   Valor retornado: {client_name}")
    
    # Mostrar link completo
    link = f"{BASE_URL}/self-checkout/{token}?lang=pt"
    print(f"\n🌐 Link completo:")
    print(f"   {link}")

if __name__ == "__main__":
    if not PASSWORD:
        print("❌ ADMIN_PASSWORD não encontrada no .env")
        exit(1)
    
    print("=" * 70)
    print("TESTE DE EXTRAÇÃO DO NOME DO CLIENTE")
    print("=" * 70)
    print()
    test_resend_and_check()
    print("\n" + "=" * 70)
