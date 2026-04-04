#!/usr/bin/env python3
import pandas as pd

# Ler um ficheiro de exemplo
df = pd.read_excel('cm-25/CM-03-2025.xlsx')

print("Colunas do ficheiro:")
print(df.columns.tolist())
print("\nPrimeiras 20 linhas:")
print(df.head(20))
