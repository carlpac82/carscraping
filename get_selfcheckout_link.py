#!/usr/bin/env python3
"""
Script para obter o link de self-checkout diretamente da base de dados
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

RA_NUMBER = "06716"
BASE_URL = "https://carscraping.up.railway.app"

def get_selfcheckout_link():
    """Obter link de self-checkout da base de dados"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL não encontrada no .env")
            return
        
        print("="*80)
        print("  OBTER LINK DE SELF-CHECKOUT")
        print("="*80)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Buscar token do RA
        cursor.execute("""
            SELECT 
                rental_agreement_number,
                license_plate,
                self_checkin_token,
                self_checkin_email,
                self_checkin_completed,
                vehicle_id,
                extracted_data
            FROM rental_agreements
            WHERE rental_agreement_number = %s
        """, (RA_NUMBER,))
        
        result = cursor.fetchone()
        
        if not result:
            print(f"\n❌ Contrato RA {RA_NUMBER} não encontrado!")
            cursor.close()
            conn.close()
            return
        
        ra_num, plate, token, email, completed, vehicle_id, extracted_data = result
        
        print(f"\n📋 DADOS DO CONTRATO:")
        print(f"   RA: {ra_num}")
        print(f"   Matrícula: {plate}")
        print(f"   Email: {email or 'Não definido'}")
        print(f"   Token: {token or 'Não gerado'}")
        print(f"   Completado: {'Sim' if completed else 'Não'}")
        
        if token:
            link = f"{BASE_URL}/self-checkin/{token}"
            print(f"\n🔗 LINK DE SELF-CHECKOUT:")
            print(f"   {link}")
            print(f"\n📧 Este link deveria ter sido enviado para: {email}")
            print(f"\n💡 PODE ABRIR ESTE LINK DIRETAMENTE NO BROWSER PARA TESTAR!")
        else:
            print(f"\n⚠️  Token não foi gerado ainda!")
            print(f"   Execute: python3 test_selfcheckout_auto.py")
        
        # Verificar se há inspeções deste RA
        cursor.execute("""
            SELECT 
                inspection_number,
                inspection_type,
                status,
                is_self_checkin,
                created_at
            FROM vehicle_inspections
            WHERE contract_number = %s OR contract_number LIKE %s
            ORDER BY created_at DESC
        """, (RA_NUMBER, f"{RA_NUMBER}%"))
        
        inspections = cursor.fetchall()
        
        if inspections:
            print(f"\n📊 INSPEÇÕES EXISTENTES ({len(inspections)}):")
            for insp in inspections:
                insp_num, insp_type, status, is_self, created = insp
                self_tag = "🚗 SELF-CHECKOUT" if is_self else "👤 MANUAL"
                print(f"   - {insp_num} | {insp_type} | {status or 'N/A'} | {self_tag} | {created}")
        else:
            print(f"\n📊 Nenhuma inspeção encontrada para este RA")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_selfcheckout_link()
