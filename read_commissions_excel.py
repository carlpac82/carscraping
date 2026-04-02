#!/usr/bin/env python3
"""
Script para ler o ficheiro CM-01-2026.xlsx e mostrar os dados das comissões
"""
import pandas as pd

def read_commissions():
    """Lê e mostra os dados do ficheiro Excel"""
    try:
        # Ler o ficheiro Excel
        df = pd.read_excel('CM-01-2026.xlsx')
        
        print("=" * 80)
        print("COMISSÕES JANEIRO 2026 - CM-01-2026")
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
        print("RESUMO POR COMISSIONISTA:")
        print("=" * 80)
        
        # Se houver coluna de comissionista e valor de comissão
        if 'Comissionista' in df.columns or 'comissionista' in df.columns:
            col_comissionista = 'Comissionista' if 'Comissionista' in df.columns else 'comissionista'
            
            # Procurar coluna de valor
            col_valor = None
            for col in df.columns:
                if 'comiss' in col.lower() or 'valor' in col.lower():
                    col_valor = col
                    break
            
            if col_valor:
                resumo = df.groupby(col_comissionista)[col_valor].agg(['sum', 'count'])
                resumo.columns = ['Total', 'Nº Reservas']
                print(resumo)
                print(f"\nTOTAL GERAL: €{resumo['Total'].sum():.2f}")
        
    except Exception as e:
        print(f"❌ Erro ao ler ficheiro: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    read_commissions()
