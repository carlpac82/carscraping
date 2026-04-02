#!/usr/bin/env python3
"""
Script para ler o ficheiro CM-02-2026.xlsx e mostrar os dados das comissões
"""
import pandas as pd

def read_commissions():
    """Lê e mostra os dados do ficheiro Excel"""
    try:
        # Ler o ficheiro Excel
        df = pd.read_excel('CM-02-2026.xlsx')
        
        print("=" * 80)
        print("COMISSÕES FEVEREIRO 2026 - CM-02-2026")
        print("=" * 80)
        print(f"\nTotal de linhas: {len(df)}")
        print(f"\nColunas: {list(df.columns)}")
        print("\n" + "=" * 80)
        print("DADOS:")
        print("=" * 80)
        
        # Mostrar todos os dados
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        print(df.to_string(index=False))
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Erro ao ler ficheiro: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    read_commissions()
