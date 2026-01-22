#!/usr/bin/env python3
"""
Script para atualizar o email do contrato AS-46-EO (RA: 06716) para testes
"""

import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Dados do contrato para teste
TEST_RA = "06716"
TEST_EMAIL = "carlpac82@hotmail.com"

def update_contract_email():
    """Atualizar email do contrato para testes"""
    try:
        # Conectar à base de dados
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL não encontrada no .env")
            return False
        
        print(f"🔌 Conectando à base de dados...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar se o contrato existe
        cursor.execute("""
            SELECT rental_agreement_number, self_checkin_email
            FROM rental_agreements
            WHERE rental_agreement_number = %s
        """, (TEST_RA,))
        
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ Contrato RA {TEST_RA} não encontrado!")
            cursor.close()
            conn.close()
            return False
        
        ra_number, current_email = result
        print(f"\n📋 Contrato encontrado:")
        print(f"   RA: {ra_number}")
        print(f"   Email atual: {current_email or 'Não definido'}")
        
        # Atualizar email
        cursor.execute("""
            UPDATE rental_agreements
            SET self_checkin_email = %s
            WHERE rental_agreement_number = %s
        """, (TEST_EMAIL, TEST_RA))
        
        conn.commit()
        
        print(f"\n✅ Email atualizado com sucesso!")
        print(f"   Novo email: {TEST_EMAIL}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao atualizar email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("  ATUALIZAR EMAIL DO CONTRATO PARA TESTES")
    print("="*60)
    
    success = update_contract_email()
    
    if success:
        print("\n" + "="*60)
        print("✅ PRONTO! Agora pode executar o script de teste:")
        print("   python test_selfcheckout_mockup.py")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Falha ao atualizar email")
        print("="*60)
