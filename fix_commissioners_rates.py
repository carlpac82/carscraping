import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

def fix_commissioners_rates():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("CORRIGIR TAXAS DE COMISSÃO NA TABELA COMMISSIONERS")
    print("=" * 80)
    
    # Obter todos os comissionistas com taxa > 1
    query = "SELECT id, name, commission_rate FROM commissioners WHERE commission_rate > 1"
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"\n📋 Total de comissionistas com taxa errada: {len(rows)}")
    
    updated_count = 0
    
    for row in rows:
        commissioner_id = row[0]
        name = row[1]
        old_rate = float(row[2])
        new_rate = old_rate / 100
        
        # Atualizar taxa
        update_query = "UPDATE commissioners SET commission_rate = %s WHERE id = %s"
        cur.execute(update_query, (new_rate, commissioner_id))
        updated_count += 1
        
        if updated_count <= 10:
            print(f"  ✓ {name}: {old_rate} → {new_rate}")
    
    if updated_count > 10:
        print(f"  ... e mais {updated_count - 10} comissionistas atualizados")
    
    # Commit
    conn.commit()
    
    print(f"\n✅ Total de taxas corrigidas: {updated_count}")
    
    # Verificar resultado
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO APÓS CORREÇÃO:")
    print("=" * 80)
    
    query = "SELECT COUNT(*) FROM commissioners WHERE commission_rate > 1"
    cur.execute(query)
    wrong_count = cur.fetchone()[0]
    
    query = "SELECT COUNT(*) FROM commissioners WHERE commission_rate <= 1 AND commission_rate > 0"
    cur.execute(query)
    correct_count = cur.fetchone()[0]
    
    print(f"\n✓ Taxas corretas (0 < taxa ≤ 1): {correct_count}")
    print(f"✗ Taxas erradas (taxa > 1): {wrong_count}")
    
    if wrong_count == 0:
        print("\n🎉 Todas as taxas foram corrigidas com sucesso!")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    fix_commissioners_rates()
