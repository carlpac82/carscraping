#!/usr/bin/env python3
import psycopg2
from werkzeug.security import generate_password_hash

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

print("🔐 RESETAR PASSWORD DO ADMIN")
print("=" * 50)
print("")

# Pedir nova password
new_password = input("Nova password para 'admin': ")

if not new_password:
    print("❌ Password não pode estar vazia!")
    exit(1)

print("")
print("🔄 Gerando hash da password...")

# Gerar hash
password_hash = generate_password_hash(new_password)

print("✅ Hash gerado")
print("")
print("🔄 Atualizando na base de dados...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Atualizar password
    cursor.execute(
        "UPDATE users SET password_hash = %s WHERE username = 'admin'",
        (password_hash,)
    )
    
    # Verificar se atualizou
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    if count > 0:
        print("✅ Password atualizada com sucesso!")
        print("")
        print(f"Credenciais:")
        print(f"  Username: admin")
        print(f"  Password: {new_password}")
        print("")
        print("Podes fazer login em: https://carscraping.up.railway.app")
    else:
        print("❌ Utilizador 'admin' não encontrado!")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
