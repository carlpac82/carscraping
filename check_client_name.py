#!/usr/bin/env python3
"""
Script para verificar o extracted_data do contrato RA 06716
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

def check_client_name():
    """Verificar extracted_data do RA 06716"""
    
    # Determinar tipo de BD
    db_url = os.getenv("DATABASE_URL", "")
    
    if "postgresql" in db_url or "postgres" in db_url:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                rental_agreement_number,
                self_checkin_email,
                extracted_data
            FROM rental_agreements
            WHERE rental_agreement_number = %s
        """, ("06716",))
    else:
        import sqlite3
        conn = sqlite3.connect("rental_data.db")
        cursor = conn.execute("""
            SELECT 
                rental_agreement_number,
                self_checkin_email,
                extracted_data
            FROM rental_agreements
            WHERE rental_agreement_number = ?
        """, ("06716",))
    
    row = cursor.fetchone()
    
    if row:
        ra_num, email, extracted_data_json = row
        print(f"RA: {ra_num}")
        print(f"Email: {email}")
        print(f"\nExtracted Data JSON:")
        print(extracted_data_json)
        
        if extracted_data_json:
            try:
                extracted_data = json.loads(extracted_data_json)
                print(f"\nExtracted Data (parsed):")
                print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
                
                client_name = extracted_data.get('client_name') or extracted_data.get('nome_cliente')
                print(f"\nClient Name: {client_name}")
            except Exception as e:
                print(f"Erro ao fazer parse: {e}")
    else:
        print("RA 06716 não encontrado")
    
    conn.close()

if __name__ == "__main__":
    check_client_name()
