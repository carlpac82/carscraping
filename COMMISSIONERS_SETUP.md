# Setup de Comissionistas - Railway

## ⚠️ IMPORTANTE: Criar Tabelas na Base de Dados

O sistema de comissionistas precisa de **2 tabelas**:
1. `commissioners` - Dados dos comissionistas
2. `bookings` - Reservas feitas pelos comissionistas

### Método 1: Script Python (RECOMENDADO)

Execute no terminal do Railway:

```bash
python init_all_tables.py
```

Este script cria **ambas** as tabelas automaticamente.

### Método 2: SQL Direto

Execute os seguintes ficheiros SQL na ordem:

```bash
# 1. Criar tabela commissioners
python -c "from database import get_db; conn = get_db(); cursor = conn.cursor(); cursor.execute(open('create_commissioners_tables.sql').read()); conn.commit(); conn.close(); print('✅ Commissioners criado!')"

# 2. Criar tabela bookings
python -c "from database import get_db; conn = get_db(); cursor = conn.cursor(); cursor.execute(open('create_bookings_table.sql').read()); conn.commit(); conn.close(); print('✅ Bookings criado!')"
```

## Adicionar Comissionistas de Teste

Após criar a tabela, pode adicionar comissionistas através da interface web em:
- `/admin/commissioners` - Gestão de comissionistas

Ou executar SQL diretamente:

```sql
INSERT INTO commissioners (name, email, username, password_hash, commission_rate, enabled)
VALUES 
    ('João Silva', 'joao@exemplo.com', 'joao', '$2b$12$...', 10.00, true),
    ('Maria Santos', 'maria@exemplo.com', 'maria', '$2b$12$...', 15.00, true);
```

## Verificar se a Tabela Existe

```bash
python -c "from database import get_db; conn = get_db(); cursor = conn.cursor(); cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name='commissioners'\"); print('Tabela existe!' if cursor.fetchone() else 'Tabela NÃO existe'); conn.close()"
```

## Estrutura da Tabela

```sql
CREATE TABLE commissioners (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    commission_rate DECIMAL(5, 2) DEFAULT 0.00,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
