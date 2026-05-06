# 🔴 DIAGNÓSTICO CRÍTICO: Problemas de Conexão PostgreSQL

## Problema Identificado

O servidor PostgreSQL Railway está a **fechar conexões prematuramente** causando:
- `SSL SYSCALL error: EOF detected`
- `server closed the connection unexpectedly`
- `current transaction is aborted`
- `connection already closed`

## Causa Raiz

### 1. **Connection Pool Esgotado**
- Railway PostgreSQL tem limite de conexões (provavelmente 20-50)
- Aplicação está a criar conexões sem as libertar corretamente
- Connection pool (3-15 por worker × 6 workers = até 90 conexões)
- **EXCEDE O LIMITE DO RAILWAY!**

### 2. **Idle Connection Timeout**
- Railway fecha conexões idle após ~60 segundos
- Aplicação não está a usar keepalive adequadamente
- Conexões ficam "mortas" mas ainda no pool

### 3. **Transações Não Commitadas**
- Muitas queries sem `commit()` ou `rollback()`
- Locks na base de dados
- Transações abortadas a bloquear novas queries

## Soluções Imediatas

### ✅ Solução 1: Reduzir Connection Pool
```python
# Em database.py, linha 51-54
connection_pool = pool.ThreadedConnectionPool(
    minconn=1,      # Era 3
    maxconn=5,      # Era 15 (5 × 6 workers = 30 total)
    **DB_CONFIG
)
```

### ✅ Solução 2: Adicionar Keepalive (JÁ IMPLEMENTADO)
```python
DB_CONFIG = {
    'keepalives': 1,
    'keepalives_idle': 30,
    'keepalives_interval': 10,
    'keepalives_count': 5,
}
```

### ✅ Solução 3: Forçar Cleanup de Conexões
```python
# Adicionar ao database.py
def cleanup_pool():
    """Limpar conexões mortas do pool"""
    if connection_pool:
        try:
            connection_pool.closeall()
            # Recriar pool
            connection_pool = pool.ThreadedConnectionPool(...)
        except:
            pass
```

### ✅ Solução 4: Usar Context Managers SEMPRE
```python
# ERRADO:
conn = get_db()
cursor = conn.cursor()
cursor.execute(...)
# Esqueceu de fechar!

# CERTO:
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute(...)
    conn.commit()
# Fecha automaticamente
```

## Problemas Específicos Encontrados

### 1. Coluna `return_location` em falta
```sql
ALTER TABLE rental_agreements 
ADD COLUMN IF NOT EXISTS return_location TEXT;
```

### 2. Queries sem tratamento de erros
```python
# main.py linha ~32000
cursor.execute("""...""")  # Sem try/except
# Se falhar, transação fica aberta!
```

### 3. Connection pool sem limite de workers
```python
# main.py linha 164
_THREAD_POOL = ThreadPoolExecutor(max_workers=50)
# 50 threads × potencialmente 2-3 conexões cada = 100-150 conexões!
```

## Plano de Ação

### 🔥 URGENTE (Fazer AGORA):

1. **Substituir `database.py` pela versão melhorada**
   ```bash
   cp database_improved.py database.py
   ```

2. **Reduzir connection pool em `database.py`**
   ```python
   minconn=1, maxconn=5  # Máximo 30 conexões total
   ```

3. **Adicionar coluna em falta via Railway Dashboard**
   - Ir a Railway → PostgreSQL → Query
   - Executar:
     ```sql
     ALTER TABLE rental_agreements ADD COLUMN IF NOT EXISTS return_location TEXT;
     ALTER TABLE rental_agreements ADD COLUMN IF NOT EXISTS pickup_location TEXT;
     ALTER TABLE rental_agreements ADD COLUMN IF NOT EXISTS pickup_date TEXT;
     ALTER TABLE rental_agreements ADD COLUMN IF NOT EXISTS return_date TEXT;
     ```

4. **Restart Railway Service**
   - Railway Dashboard → Service → Restart
   - Limpa todas as conexões mortas

### 📋 MÉDIO PRAZO (Próximos dias):

1. **Auditar todas as queries em `main.py`**
   - Procurar por `cursor.execute` sem `try/except`
   - Adicionar `conn.commit()` ou `conn.rollback()`

2. **Implementar connection health check**
   ```python
   def is_connection_alive(conn):
       try:
           cursor = conn.cursor()
           cursor.execute("SELECT 1")
           cursor.close()
           return True
       except:
           return False
   ```

3. **Adicionar monitoring de conexões**
   ```python
   def get_pool_stats():
       if connection_pool:
           return {
               'size': connection_pool.maxconn,
               'available': len(connection_pool._pool),
               'used': connection_pool.maxconn - len(connection_pool._pool)
           }
   ```

### 🎯 LONGO PRAZO (Próximas semanas):

1. **Migrar para PgBouncer**
   - Connection pooling externo
   - Melhor gestão de conexões
   - Suporta milhares de conexões

2. **Implementar retry logic global**
   - Decorator para todas as queries
   - Exponential backoff
   - Circuit breaker pattern

3. **Separar read/write connections**
   - Pool separado para leituras
   - Pool separado para escritas
   - Melhor performance

## Comandos Úteis

### Ver conexões ativas no PostgreSQL:
```sql
SELECT count(*) FROM pg_stat_activity;
SELECT pid, usename, application_name, state, query 
FROM pg_stat_activity 
WHERE datname = 'railway';
```

### Matar conexões idle:
```sql
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND state_change < NOW() - INTERVAL '5 minutes';
```

### Ver locks:
```sql
SELECT * FROM pg_locks WHERE NOT granted;
```

## Resumo

**Problema:** Railway PostgreSQL tem limite de ~20-50 conexões, mas aplicação tenta usar até 90.

**Solução Rápida:** 
1. Reduzir pool para `maxconn=5` (30 total)
2. Adicionar colunas em falta
3. Restart service

**Solução Permanente:**
1. Usar `database_improved.py`
2. Auditar queries
3. Implementar PgBouncer

---

**Status:** 🔴 CRÍTICO - Requer ação imediata
**Prioridade:** P0 - Bloqueador
**ETA Fix:** 15 minutos
