#!/usr/bin/env python3
"""
Script para reenviar link de self-checkout para RA 06716
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração
BASE_URL = "https://rentalprices.pt"
RA_NUMBER = "06716"

# Credenciais de autenticação
USERNAME = os.getenv("ADMIN_USERNAME", "admin")
PASSWORD = os.getenv("ADMIN_PASSWORD")

if not PASSWORD:
    print("❌ ADMIN_PASSWORD não encontrada no .env")
    exit(1)

def resend_link():
    """Reenviar link de self-checkout"""
    
    # Login
    print(f"🔐 Fazendo login como {USERNAME}...")
    login_response = requests.post(
        f"{BASE_URL}/api/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.status_code}")
        print(login_response.text)
        return
    
    cookies = login_response.cookies
    print("✅ Login bem-sucedido")
    
    # Reenviar link
    print(f"\n📧 Reenviando link para RA {RA_NUMBER}...")
    resend_response = requests.post(
        f"{BASE_URL}/api/self-checkin/resend-link",
        json={"rental_agreement_number": RA_NUMBER},
        cookies=cookies
    )
    
    if resend_response.status_code == 200:
        data = resend_response.json()
        print(f"✅ Link reenviado com sucesso!")
        print(f"📧 Email enviado para: {data.get('email', 'N/A')}")
        print(f"🔗 Token: {data.get('token', 'N/A')[:20]}...")
        
        # Construir link completo
        token = data.get('token', '')
        if token:
            link = f"{BASE_URL}/self-checkout/{token}?lang=pt"
            print(f"\n🌐 Link completo:")
            print(f"   {link}")
    else:
        print(f"❌ Erro ao reenviar: {resend_response.status_code}")
        print(resend_response.text)

if __name__ == "__main__":
    print("=" * 60)
    print("REENVIAR LINK DE SELF-CHECKOUT")
    print("=" * 60)
    resend_link()
    print("\n" + "=" * 60)
