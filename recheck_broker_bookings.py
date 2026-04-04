import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def recheck_broker_bookings():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("VERIFICAR TODAS AS COLUNAS DE broker_bookings")
    print("=" * 80)
    
    # Verificar TODAS as colunas
    query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'broker_bookings'
        ORDER BY ordinal_position
    """
    
    cur.execute(query)
    columns = cur.fetchall()
    
    print("\nTODAS AS COLUNAS:")
    for col in columns:
        print(f"  {col[0]:<30} {col[1]:<20} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
    
    # Procurar especificamente por 'base'
    print("\n" + "=" * 80)
    print("COLUNAS COM 'base' NO NOME:")
    print("=" * 80)
    
    base_columns = [col for col in columns if 'base' in col[0].lower()]
    if base_columns:
        for col in base_columns:
            print(f"  ✓ {col[0]}")
    else:
        print("  ❌ Nenhuma coluna com 'base' encontrada")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    recheck_broker_bookings()
