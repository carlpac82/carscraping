# Setup de Comissionistas - Railway

## Criar Tabela na Base de Dados

Para criar a tabela `commissioners` na base de dados PostgreSQL do Railway, execute o seguinte comando no terminal do Railway:

```bash
python init_commissioners_db.py
```

Ou execute diretamente o SQL:

```bash
python -c "from database import get_db; conn = get_db(); cursor = conn.cursor(); cursor.execute(open('create_commissioners_tables.sql').read()); conn.commit(); conn.close(); print('✅ Tabelas criadas com sucesso!')"
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
