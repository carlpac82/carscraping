import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def check_commissioners_rates():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("VERIFICAR TAXAS DE COMISSÃO NA TABELA COMMISSIONERS")
    print("=" * 80)
    
    query = "SELECT id, name, commission_rate FROM commissioners ORDER BY name"
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"\n{'ID':<5} {'Nome':<30} {'Taxa':<10} {'Formato':<15}")
    print("-" * 80)
    
    wrong_format = []
    
    for row in rows:
        commissioner_id = row[0]
        name = row[1]
        rate = float(row[2]) if row[2] else 0
        
        # Verificar formato
        if rate > 1:
            format_status = "❌ ERRADO (>1)"
            wrong_format.append((commissioner_id, name, rate))
        else:
            format_status = "✓ Correto"
        
        print(f"{commissioner_id:<5} {name:<30} {rate:<10.2f} {format_status:<15}")
    
    if wrong_format:
        print("\n" + "=" * 80)
        print(f"⚠️  ENCONTRADOS {len(wrong_format)} COMISSIONISTAS COM TAXA ERRADA")
        print("=" * 80)
        print("\nEstas taxas devem ser divididas por 100 (ex: 15.0 → 0.15)")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_commissioners_rates()
