#!/usr/bin/env python3
"""
Script para importar dados de comissões de 2025 dos arquivos Excel
"""
import pandas as pd
import sqlite3
from datetime import datetime
import os
from pathlib import Path

def parse_date(date_str):
    """Converter string de data para datetime"""
    if pd.isna(date_str):
        return None
    if isinstance(date_str, datetime):
        return date_str
    try:
        return pd.to_datetime(date_str)
    except:
        return None

def get_commissioner_mapping():
    """Mapeamento de nomes de comissionistas para IDs"""
    # Mapeamento baseado nos dados existentes - ajustar conforme necessário
    return {
        'ANA': 1,
        'ANA PAULA': 1,
        'CARLA': 2,
        'CARLA MIRANDA': 2,
        'CRISTINA': 3,
        'CRISTINA SILVA': 3,
        'SANDRA': 4,
        'SANDRA COSTA': 4,
        'MARGARIDA': 5,
        'MARGARIDA SANTOS': 5,
        'JOANA': 6,
        'JOANA FERREIRA': 6,
        'SOFIA': 7,
        'SOFIA MARTINS': 7,
        'INÊS': 8,
        'INÊS GOMES': 8,
        'MARIA': 9,
        'MARIA OLIVEIRA': 9,
        'CATARINA': 10,
        'CATARINA DIAS': 10,
    }

def extract_commissioner_name(voucher):
    """Extrair nome do comissionista do voucher"""
    if pd.isna(voucher):
        return None
    voucher_str = str(voucher).strip()
    
    # Lista de nomes conhecidos
    commissioner_names = [
        'ANA', 'ANA PAULA', 'CARLA', 'CARLA MIRANDA', 'CRISTINA', 'CRISTINA SILVA',
        'SANDRA', 'SANDRA COSTA', 'MARGARIDA', 'MARGARIDA SANTOS', 'JOANA', 'JOANA FERREIRA',
        'SOFIA', 'SOFIA MARTINS', 'INÊS', 'INÊS GOMES', 'MARIA', 'MARIA OLIVEIRA',
        'CATARINA', 'CATARINA DIAS'
    ]
    
    for name in commissioner_names:
        if name in voucher_str.upper():
            return name
    
    return None

def calculate_commission_amount(days, loyalty_card):
    """Calcular valor da comissão baseado nos dias e cartão loyalty"""
    if pd.isna(days) or pd.isna(loyalty_card):
        return 0.0
    
    try:
        days = float(days)
        loyalty_card = float(loyalty_card)
        # Regra: 20% do valor do loyalty card
        commission = loyalty_card * 0.2
        return round(commission, 2)
    except:
        return 0.0

def import_monthly_commissions(file_path, month, year):
    """Importar comissões de um arquivo mensal"""
    print(f"Importando {file_path}...")
    
    try:
        df = pd.read_excel(file_path)
        print(f"  - Arquivo lido: {len(df)} linhas")
        
        # Conectar ao banco de dados
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS commission_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voucher TEXT,
            pickup_date DATETIME,
            days REAL,
            loyalty_card REAL,
            commission_amount REAL,
            commission_paid BOOLEAN DEFAULT FALSE,
            commissioner_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        commissioner_mapping = get_commissioner_mapping()
        imported_count = 0
        
        for index, row in df.iterrows():
            # Pular linhas vazias
            if pd.isna(row['Voucher']) and pd.isna(row['Data Entrega']):
                continue
            
            # Extrair dados
            voucher = row['Voucher'] if not pd.isna(row['Voucher']) else None
            pickup_date = parse_date(row['Data Entrega'])
            days = row['Dias'] if not pd.isna(row['Dias']) else None
            loyalty_card = row['Loyalty Card'] if not pd.isna(row['Loyalty Card']) else None
            
            # Pular se não houver data de entrega
            if pickup_date is None:
                continue
            
            # Extrair nome do comissionista
            commissioner_name = extract_commissioner_name(voucher)
            commissioner_id = commissioner_mapping.get(commissioner_name) if commissioner_name else None
            
            # Calcular comissão
            commission_amount = calculate_commission_amount(days, loyalty_card)
            
            # Inserir no banco de dados
            cursor.execute("""
            INSERT INTO commission_bookings 
            (voucher, pickup_date, days, loyalty_card, commission_amount, commissioner_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(voucher) if voucher is not None else None,
                pickup_date.isoformat() if pickup_date is not None else None,
                float(days) if days is not None else None,
                float(loyalty_card) if loyalty_card is not None else None,
                float(commission_amount),
                int(commissioner_id) if commissioner_id is not None else None
            ))
            
            imported_count += 1
            
            if imported_count <= 5:  # Mostrar primeiros registros
                print(f"    Registro {imported_count}: {voucher} - {pickup_date} - €{commission_amount}")
        
        conn.commit()
        conn.close()
        
        print(f"  - Importados {imported_count} registros")
        return imported_count
        
    except Exception as e:
        print(f"  - Erro: {e}")
        return 0

def main():
    """Função principal"""
    print("=== Importação de Comissões 2025 ===")
    
    # Diretório dos arquivos
    excel_dir = Path("/Users/filipepacheco/CascadeProjects/carscraping/2025")
    
    if not excel_dir.exists():
        print(f"Erro: Diretório {excel_dir} não encontrado!")
        return
    
    total_imported = 0
    
    # Processar todos os arquivos Excel em ordem
    excel_files = sorted(excel_dir.glob("CM-*.xlsx"))
    
    print(f"Encontrados {len(excel_files)} arquivos:")
    for file_path in excel_files:
        print(f"  - {file_path.name}")
    
    print("\nIniciando importação...")
    
    for file_path in excel_files:
        # Extrair mês e ano do nome do arquivo
        parts = file_path.stem.split('-')
        if len(parts) >= 3:
            month = int(parts[1])
            year = int(parts[2])
            
            count = import_monthly_commissions(file_path, month, year)
            total_imported += count
    
    print(f"\n=== Resumo ===")
    print(f"Total de registros importados: {total_imported}")
    print("Importação concluída!")

if __name__ == "__main__":
    main()
