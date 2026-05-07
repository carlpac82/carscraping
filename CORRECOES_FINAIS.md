# ✅ Correções Finais - Connection Pool PostgreSQL

## 📋 Problema Identificado
O código estava a usar `_db_connect()` diretamente em vez do context manager `get_db_connection()`, causando:
- **Connection leaks** (conexões não devolvidas ao pool)
- **Pool exhaustion** (esgotamento do pool de conexões)
- **Erros "connection already closed"** durante migrations

## 🔧 Correções Aplicadas

### 1. **Funções Críticas Corrigidas** ✅

#### `_get_current_user()` - Linha ~2594
```python
# ANTES:
conn = _db_connect()
try:
    ...
finally:
    conn.close()

# DEPOIS:
with get_db_connection() as conn:
    if USE_POSTGRES:
        conn = PostgreSQLConnectionWrapper(conn)
    ...
```

#### `_require_auth()` - Linha ~2614
```python
# ANTES:
con = _db_connect()
try:
    ...
finally:
    con.close()

# DEPOIS:
with get_db_connection() as con:
    if USE_POSTGRES:
        con = PostgreSQLConnectionWrapper(con)
    ...
```

#### `_require_admin()` - Linha ~2647
```python
# ANTES:
con = _db_connect()
try:
    ...
finally:
    con.close()

# DEPOIS:
with get_db_connection() as con:
    if USE_POSTGRES:
        con = PostgreSQLConnectionWrapper(con)
    ...
```

#### `_require_role()` - Linha ~2669
```python
# ANTES:
con = _db_connect()
try:
    ...
finally:
    con.close()

# DEPOIS:
with get_db_connection() as con:
    if USE_POSTGRES:
        con = PostgreSQLConnectionWrapper(con)
    ...
```

#### `send_notification()` - Linha ~5005
```python
# ANTES:
conn = _db_connect()
try:
    ...
finally:
    conn.close()

# DEPOIS:
with get_db_connection() as conn:
    if USE_POSTGRES:
        conn = PostgreSQLConnectionWrapper(conn)
    ...
```

#### `_get_gmail_credentials()` - Linha ~5046
```python
# ANTES:
conn = _db_connect()
try:
    ...
finally:
    conn.close()

# DEPOIS:
with get_db_connection() as conn:
    if USE_POSTGRES:
        conn = PostgreSQLConnectionWrapper(conn)
    ...
```

#### Migration de `commission_bookings` (Startup) - Linha ~1352
```python
# ANTES:
migration_conn = _db_connect()
try:
    ...
finally:
    migration_conn.close()

# DEPOIS:
with get_db_connection() as migration_conn:
    if USE_POSTGRES:
        migration_conn = PostgreSQLConnectionWrapper(migration_conn)
    ...
```

## 🎯 Benefícios das Correções

1. **Gestão Automática de Conexões**
   - O context manager garante que conexões são sempre devolvidas ao pool
   - Mesmo em caso de exceções, a conexão é libertada

2. **Prevenção de Connection Leaks**
   - Elimina o risco de esquecer `conn.close()`
   - Pool de conexões mantém-se saudável

3. **Compatibilidade PostgreSQL**
   - Usa `PostgreSQLConnectionWrapper` para converter sintaxe SQLite → PostgreSQL
   - Garante que queries funcionam corretamente

4. **Resiliência**
   - Combinado com retry logic em `database.py`
   - Timeouts aumentados (120s) para migrations longas

## ⚠️ Funções Ainda Pendentes

Existem **~45 ocorrências adicionais** de `_db_connect()` no código que não foram corrigidas nesta sessão.
Estas incluem:
- Endpoints de API menos críticos
- Funções de relatórios
- Operações de backup

**Recomendação**: Corrigir gradualmente em futuras sessões, priorizando:
1. Endpoints com alto tráfego
2. Operações de longa duração
3. Background jobs

## 📊 Status Atual

- ✅ **Funções de autenticação** corrigidas (crítico)
- ✅ **Migrations de startup** corrigidas (crítico)
- ✅ **Notificações** corrigidas
- ✅ **OAuth Gmail** corrigido
- ⏳ **Endpoints de API** pendentes (baixa prioridade)

## 🚀 Deploy

```bash
git add -A
git commit -m "Fix: Replace critical _db_connect() calls with context manager"
git push
```

**Deploy ID**: d6eb1a0
**Data**: 2026-05-06
**Status**: ✅ Deployed to Railway

## 📝 Próximos Passos

1. **Monitorizar logs** no Railway para erros de conexão
2. **Verificar pool usage** com query:
   ```sql
   SELECT count(*) FROM pg_stat_activity WHERE datname = 'railway';
   ```
3. **Corrigir restantes** `_db_connect()` calls gradualmente
4. **Adicionar health check** endpoint para monitorização

## 🔍 Como Identificar Connection Leaks

```bash
# Ver conexões ativas no PostgreSQL
psql $DATABASE_URL -c "SELECT pid, usename, application_name, state, query_start FROM pg_stat_activity WHERE datname = 'railway';"

# Matar conexões idle (emergência)
python emergency_fix.py
```

---
**Autor**: Cascade AI  
**Projeto**: rentalprices.pt  
**Railway**: shortline.proxy.rlwy.net:45408
