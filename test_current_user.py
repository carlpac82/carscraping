#!/usr/bin/env python3
"""
Script para testar se a função _get_user_by_username retorna os dados corretos
"""
import sys
import os
sys.path.append('/Users/filipepacheco/CascadeProjects/carscraping')

from dotenv import load_dotenv
import psycopg2

# Importar as funções do main.py
from main import _db_connect, _get_user_by_username

def test_get_user_by_username():
    load_dotenv()
    
    # Testar com o user LP
    username = "LP"
    print(f"Testando _get_user_by_username para o user '{username}':")
    
    user_data = _get_user_by_username(username)
    
    if user_data:
        print("User encontrado:")
        for key, value in user_data.items():
            print(f"  {key}: {value}")
    else:
        print("User não encontrado")
    
    return user_data

if __name__ == "__main__":
    test_get_user_by_username()
