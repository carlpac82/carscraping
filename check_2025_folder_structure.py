#!/usr/bin/env python3
import pandas as pd

# Ler um ficheiro de exemplo da pasta 2025
df = pd.read_excel('2025/CM-03-2025.xlsx')

print("Colunas do ficheiro:")
print(df.columns.tolist())
print("\nPrimeiras 20 linhas:")
print(df.head(20))
