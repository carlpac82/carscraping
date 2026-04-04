import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def delete_jan_feb_2026():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("APAGAR DADOS DE JANEIRO E FEVEREIRO 2026")
    print("=" * 80)
    
    for month in [1, 2]:
        month_name = 'Janeiro' if month == 1 else 'Fevereiro'
        
        # Verificar quantos registos existem
        query = """
            SELECT COUNT(*) 
            FROM commission_bookings 
            WHERE EXTRACT(YEAR FROM pickup_date) = 2026 
            AND EXTRACT(MONTH FROM pickup_date) = %s
        """
        cur.execute(query, (month,))
        count = cur.fetchone()[0]
        
        print(f"\n{month_name}: {count} registos encontrados")
        
        if count > 0:
            # Apagar
            delete_query = """
                DELETE FROM commission_bookings 
                WHERE EXTRACT(YEAR FROM pickup_date) = 2026 
                AND EXTRACT(MONTH FROM pickup_date) = %s
            """
            cur.execute(delete_query, (month,))
            print(f"✅ {count} registos apagados")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ CONCLUÍDO")
    print("=" * 80)

if __name__ == "__main__":
    delete_jan_feb_2026()
