#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

def check_user_permissions():
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL não encontrada no .env")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar permissões do user LP (assumindo que seja username 'LP')
        cursor.execute("""
            SELECT id, username, role, can_manage_commissioners, can_manage_commissions, has_commissioner_access
            FROM users 
            WHERE username ILIKE '%LP%' OR username ILIKE '%lp%'
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("User 'LP' não encontrado. A verificar todos os users:")
            cursor.execute("""
                SELECT id, username, role, can_manage_commissioners, can_manage_commissions, has_commissioner_access
                FROM users 
                WHERE role = 'support'
                ORDER BY username
            """)
            
            results = cursor.fetchall()
            
            if results:
                print("\nUsers com role 'support':")
                for row in results:
                    print(f"  ID: {row[0]}, Username: {row[1]}, Role: {row[2]}")
                    print(f"    can_manage_commissioners: {row[3]}")
                    print(f"    can_manage_commissions: {row[4]}")
                    print(f"    has_commissioner_access: {row[5]}")
                    print()
            else:
                print("Nenhum user com role 'support' encontrado")
        else:
            print("Dados do user 'LP':")
            for row in results:
                print(f"  ID: {row[0]}, Username: {row[1]}, Role: {row[2]}")
                print(f"    can_manage_commissioners: {row[3]}")
                print(f"    can_manage_commissions: {row[4]}")
                print(f"    has_commissioner_access: {row[5]}")
        
        return True
        
    except Exception as e:
        print(f"Erro: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_user_permissions()
