"""
Script de debug para verificar preços dos comissionistas
"""
import os
import sys

# Set DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway'
os.environ['USE_POSTGRES'] = 'true'

sys.path.insert(0, '.')

from database import get_db

def test_pricing():
    conn = get_db()
    cur = conn.cursor()
    
    # Buscar preço para Grupo B, época média, 3 dias
    key = 'commissioner_season_B_mid_day3'
    
    cur.execute("SELECT setting_value FROM settings WHERE setting_key = %s", (key,))
    row = cur.fetchone()
    
    print('🔍 TESTE DE PREÇOS - GRUPO B, ÉPOCA MÉDIA, 3 DIAS')
    print('=' * 60)
    print(f'Chave: {key}')
    
    if row:
        price = row[0]
        print(f'✅ Valor encontrado: {price}€')
    else:
        print('❌ Valor NÃO encontrado na tabela settings')
        
    print()
    
    # Buscar todos os preços de Grupo B, época média
    print('📊 TODOS OS PREÇOS - GRUPO B, ÉPOCA MÉDIA:')
    print('=' * 60)
    
    for day in range(1, 8):
        key = f'commissioner_season_B_mid_day{day}'
        cur.execute("SELECT setting_value FROM settings WHERE setting_key = %s", (key,))
        row = cur.fetchone()
        if row:
            print(f'  day{day}: {row[0]}€')
        else:
            print(f'  day{day}: NÃO ENCONTRADO')
    
    print()
    
    # Buscar seguro para Grupo B, época média, 3-7 dias
    insurance_key = 'commissioner_insurance_B_mid_3_7_days'
    cur.execute("SELECT setting_value FROM settings WHERE setting_key = %s", (insurance_key,))
    row = cur.fetchone()
    
    print('🛡️ SEGURO PREMIUM - GRUPO B, ÉPOCA MÉDIA, 3-7 DIAS:')
    print('=' * 60)
    print(f'Chave: {insurance_key}')
    
    if row:
        insurance_price = row[0]
        print(f'✅ Valor encontrado: {insurance_price}€/dia')
        print(f'   Para 3 dias: {float(insurance_price) * 3}€')
    else:
        print('❌ Valor NÃO encontrado')
    
    conn.close()

if __name__ == '__main__':
    test_pricing()
