#!/usr/bin/env python3
"""
Mockup completo do processo de Self-Checkout
Contrato: AS-46-EO (RA: 06716)
Email de teste: carlpac82@hotmail.com
"""

import requests
import json
import base64
from datetime import datetime

# Configuração
BASE_URL = "https://carscraping.up.railway.app"  # ou "http://localhost:8000" para local
RA_NUMBER = "06716"
PLATE = "AS-46-EO"
TEST_EMAIL = "carlpac82@hotmail.com"

# Credenciais de autenticação (se necessário)
AUTH_USERNAME = "admin"  # ajustar conforme necessário
AUTH_PASSWORD = "your_password"  # ajustar conforme necessário

def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def update_contract_email():
    """Passo 1: Atualizar email do contrato para teste"""
    print_section("PASSO 1: Atualizar Email do Contrato")
    
    print(f"📧 Atualizando contrato {RA_NUMBER} com email: {TEST_EMAIL}")
    
    # SQL direto para atualizar (executar manualmente ou via endpoint)
    sql_update = f"""
    UPDATE rental_agreements 
    SET self_checkin_email = '{TEST_EMAIL}'
    WHERE rental_agreement_number = '{RA_NUMBER}';
    """
    
    print("\n🔧 SQL para executar manualmente:")
    print(sql_update)
    print("\n✅ Execute este SQL na base de dados antes de continuar")
    input("\nPressione ENTER quando tiver executado o SQL...")

def generate_selfcheckout_link():
    """Passo 2: Gerar link de self-checkout"""
    print_section("PASSO 2: Gerar Link de Self-Checkout")
    
    url = f"{BASE_URL}/api/self-checkin/generate-link"
    
    payload = {
        "ra_number": RA_NUMBER,
        "client_email": TEST_EMAIL
    }
    
    print(f"📤 POST {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\n📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                link = data.get('link')
                token = data.get('token')
                print(f"✅ Link gerado com sucesso!")
                print(f"🔗 Link: {link}")
                print(f"🎫 Token: {token}")
                return token
            else:
                print(f"❌ Erro: {data.get('error')}")
        else:
            print(f"❌ Erro HTTP: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {e}")
    
    return None

def simulate_selfcheckout_submission(token):
    """Passo 3: Simular submissão de self-checkout"""
    print_section("PASSO 3: Simular Submissão de Self-Checkout")
    
    if not token:
        print("❌ Token não disponível. Gere o link primeiro.")
        return None
    
    url = f"{BASE_URL}/api/self-checkin/{token}/submit"
    
    # Dados de exemplo para submissão
    payload = {
        "odometer": 45320,
        "fuel_level": 100,
        "photos": {
            "front": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",  # Base64 truncado
            "rear": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
            "left": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
            "right": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
            "dashboard": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
            "interior": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
            "trunk": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
            "roof": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
            "other": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
        },
        "damage_photos": []
    }
    
    print(f"📤 POST {url}")
    print(f"📦 Odómetro: {payload['odometer']} km")
    print(f"⛽ Combustível: {payload['fuel_level']}%")
    print(f"📸 Fotos: {len(payload['photos'])} fotos da grid")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\n📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                inspection_number = data.get('inspection_number')
                print(f"✅ Self-checkout submetido com sucesso!")
                print(f"🔍 Número de inspeção: {inspection_number}")
                print(f"📧 Email 'Self-Checkout Submetido' enviado para: {TEST_EMAIL}")
                return inspection_number
            else:
                print(f"❌ Erro: {data.get('error')}")
        else:
            print(f"❌ Erro HTTP: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {e}")
    
    return None

def validate_selfcheckout(inspection_number):
    """Passo 4: Validar self-checkout (envia email de validação)"""
    print_section("PASSO 4: Validar Self-Checkout")
    
    if not inspection_number:
        print("❌ Número de inspeção não disponível.")
        return False
    
    url = f"{BASE_URL}/api/self-checkin/validate"
    
    payload = {
        "inspection_number": inspection_number
    }
    
    print(f"📤 POST {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\n📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Self-checkout validado com sucesso!")
                print(f"📧 Email 'Self-Checkout Validado' enviado para: {TEST_EMAIL}")
                print(f"🎉 Contrato encerrado!")
                return True
            else:
                print(f"❌ Erro: {data.get('error')}")
        else:
            print(f"❌ Erro HTTP: {response.text}")
    except Exception as e:
        print(f"❌ Exceção: {e}")
    
    return False

def test_warning_email():
    """Passo 5: Testar email de advertência (divergências)"""
    print_section("PASSO 5: Testar Email de Advertência")
    
    print("⚠️  Para testar o email de divergências, você precisa:")
    print("1. Criar uma nova submissão de self-checkout")
    print("2. Em vez de validar, usar um endpoint de 'invalidar' ou 'advertir'")
    print("\n📝 NOTA: Atualmente não existe endpoint específico para enviar email de advertência.")
    print("   Você precisará criar um endpoint /api/self-checkin/warn ou similar")
    print("   que envie o email usando os templates email_selfcheckout_warning_*.html")

def check_history_ui():
    """Passo 6: Verificar UI do histórico"""
    print_section("PASSO 6: Verificar UI do Histórico")
    
    print("🔍 Verificando funcionalidades do histórico de inspeções...")
    print("\n✅ FUNCIONALIDADES EXISTENTES:")
    print("   - Botão 'Validar' (azul) para self-checkout pendente")
    print("   - Botão 'Invalidar' (laranja) para self-checkout pendente")
    print("   - Botão 'Reenviar Link' (roxo) para self-checkout")
    print("   - Botão 'Email' (amarelo) para enviar relatórios")
    print("   - Botão 'Parque' (azul) para QR code de parque")
    print("   - Botão 'Eliminar' (vermelho) para admin")
    print("   - Ícone de carro VERDE para Check-in (Entrega)")
    print("   - Ícone de carro VERMELHO para Check-out (Recolha)")
    
    print("\n⚠️  FUNCIONALIDADES EM FALTA:")
    print("   1. Endpoint para enviar email de advertência (divergências)")
    print("   2. Botão 'Advertir' no histórico para enviar email de divergências")
    print("   3. Indicador visual de status (pendente/validado/com divergências)")
    print("   4. Badge ou tag mostrando se é self-checkout vs inspeção manual")
    print("   5. Filtro para mostrar apenas self-checkouts")
    print("   6. Contador de self-checkouts pendentes de validação")

def create_missing_features_list():
    """Criar lista de funcionalidades em falta"""
    print_section("FUNCIONALIDADES EM FALTA - LISTA COMPLETA")
    
    missing_features = """
📋 LISTA DE FUNCIONALIDADES EM FALTA:

1. BACKEND - Endpoint de Advertência
   ❌ POST /api/self-checkin/warn
   - Recebe inspection_number
   - Envia email usando templates email_selfcheckout_warning_*.html
   - Marca inspeção com status 'warned' ou 'discrepancies'
   - Não fecha o contrato

2. FRONTEND - Botão de Advertir no Histórico
   ❌ Botão "Advertir" (laranja/amarelo)
   - Aparece junto com "Validar" e "Invalidar"
   - Chama endpoint /api/self-checkin/warn
   - Mostra confirmação antes de enviar

3. UI - Indicadores Visuais de Status
   ❌ Badge de status na card do contrato
   - "Pendente" (amarelo)
   - "Validado" (verde)
   - "Com Divergências" (laranja)
   - "Invalidado" (vermelho)

4. UI - Badge Self-Checkout
   ❌ Tag "SELF-CHECKOUT" na card
   - Distinguir de inspeções manuais
   - Cor diferenciada (roxo/azul)

5. UI - Filtros e Pesquisa
   ❌ Filtro "Apenas Self-Checkouts"
   ❌ Filtro por status (Pendente/Validado/etc)
   ❌ Contador de pendentes no topo

6. EMAILS - Função de Envio de Advertência
   ❌ Função _send_self_checkout_warning_email()
   - Similar a _send_self_checkin_confirmation_email
   - Usa templates email_selfcheckout_warning_*.html
   - Suporta PT/EN/FR

7. DATABASE - Campo de Status
   ❌ Adicionar campo 'warning_sent' em vehicle_inspections
   ❌ Adicionar campo 'discrepancy_notes' para observações

8. HISTÓRICO - Ícones Monocromáticos
   ⚠️  Atualmente os ícones de carro são COLORIDOS
   - Verde para Check-in (Entrega)
   - Vermelho para Check-out (Recolha)
   ❓ Confirmar se devem ser monocromáticos

9. NOTIFICAÇÕES
   ❌ Notificação quando self-checkout é submetido
   ❌ Notificação quando self-checkout precisa validação
   ❌ Dashboard com métricas de self-checkout

10. LOGS E AUDITORIA
    ❌ Log de quem validou/invalidou/advertiu
    ❌ Timestamp de cada ação
    ❌ Histórico de emails enviados
"""
    
    print(missing_features)
    
    # Salvar em arquivo
    with open('/Users/filipepacheco/CascadeProjects/carscraping/FUNCIONALIDADES_EM_FALTA.md', 'w', encoding='utf-8') as f:
        f.write(missing_features)
    
    print("\n💾 Lista salva em: FUNCIONALIDADES_EM_FALTA.md")

def main():
    """Executar mockup completo"""
    print("\n" + "🚗"*40)
    print("  MOCKUP COMPLETO - PROCESSO DE SELF-CHECKOUT")
    print("  Contrato: AS-46-EO (RA: 06716)")
    print("  Email: carlpac82@hotmail.com")
    print("🚗"*40)
    
    # Passo 1: Atualizar email
    update_contract_email()
    
    # Passo 2: Gerar link
    token = generate_selfcheckout_link()
    
    if token:
        # Passo 3: Submeter self-checkout
        inspection_number = simulate_selfcheckout_submission(token)
        
        if inspection_number:
            # Passo 4: Validar (envia email de validação)
            print("\n⏸️  Aguarde alguns segundos para verificar o email de submissão...")
            input("Pressione ENTER para continuar com a validação...")
            validate_selfcheckout(inspection_number)
    
    # Passo 5: Info sobre email de advertência
    test_warning_email()
    
    # Passo 6: Verificar UI
    check_history_ui()
    
    # Criar lista de funcionalidades em falta
    create_missing_features_list()
    
    print_section("MOCKUP CONCLUÍDO")
    print("✅ Verifique o email carlpac82@hotmail.com para os emails recebidos")
    print("📋 Consulte FUNCIONALIDADES_EM_FALTA.md para a lista completa")

if __name__ == "__main__":
    main()
