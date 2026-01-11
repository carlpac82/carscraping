#!/usr/bin/env python3
import psycopg2

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

print("🔄 Limpando base de dados Railway...")
print("")

try:
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("⚠️  Apagando schema public...")
    cursor.execute("DROP SCHEMA public CASCADE;")
    
    print("✅ Schema apagado")
    print("🔄 Criando schema novo...")
    cursor.execute("CREATE SCHEMA public;")
    
    print("✅ Schema criado")
    print("🔄 Configurando permissões...")
    cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
    cursor.execute("GRANT ALL ON SCHEMA public TO public;")
    
    cursor.close()
    conn.close()
    
    print("")
    print("✅ Base de dados limpa com sucesso!")
    print("")
    print("Próximo passo:")
    print("1. Ir para Railway > carscraping service")
    print("2. Deployments tab > ⋮ > Redeploy")
    print("3. Aguardar deploy completar")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    exit(1)
