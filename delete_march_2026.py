import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def delete_march_2026():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("APAGAR DADOS DE MARÇO 2026")
    print("=" * 80)
    
    # Verificar quantos registos existem
    query = """
        SELECT COUNT(*) 
        FROM commission_bookings 
        WHERE EXTRACT(YEAR FROM pickup_date) = 2026 
        AND EXTRACT(MONTH FROM pickup_date) = 3
    """
    cur.execute(query)
    count = cur.fetchone()[0]
    
    print(f"\n📋 Registos encontrados: {count}")
    
    if count > 0:
        # Apagar
        delete_query = """
            DELETE FROM commission_bookings 
            WHERE EXTRACT(YEAR FROM pickup_date) = 2026 
            AND EXTRACT(MONTH FROM pickup_date) = 3
        """
        cur.execute(delete_query)
        conn.commit()
        
        print(f"✅ {count} registos apagados")
    else:
        print("ℹ️  Nenhum registo para apagar")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    delete_march_2026()
