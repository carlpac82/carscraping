# 🛡️ SOLUÇÃO PERMANENTE - Prevenir Problemas de Conexão

## 3 Níveis de Proteção:

### 1️⃣ AUTO-CLEANUP (A CADA 5 MINUTOS)
Adicionar ao `main.py` no startup da aplicação:

```python
# No início do main.py, após os imports
from auto_cleanup_connections import start_connection_cleanup_scheduler

# Depois da criação do app FastAPI, adicionar:
@app.on_event("startup")
async def startup_event():
    # ... código existente ...
    
    # NOVO: Iniciar auto-cleanup de conexões
    start_connection_cleanup_scheduler()
```

**O que faz:**
- A cada 5 minutos, mata conexões idle há mais de 5 minutos
- Alerta se conexões > 40 (próximo do limite de 50)
- Previne acumulação de conexões mortas

---

### 2️⃣ MELHORAR database.py (Connection Wrapper)

Substituir o `database.py` atual por esta versão melhorada:

```python
# Em database.py, adicionar timeout automático

DB_CONFIG = {
    'host': result.hostname,
    'port': result.port,
    'database': result.path[1:],
    'user': result.username,
    'password': result.password,
    'sslmode': 'require',
    'connect_timeout': 10,
    'keepalives': 1,
    'keepalives_idle': 30,
    'keepalives_interval': 10,
    'keepalives_count': 5,
    'options': '-c statement_timeout=30000 -c idle_in_transaction_session_timeout=60000'
}
```

**O que faz:**
- `statement_timeout=30000` → Mata queries > 30s
- `idle_in_transaction_session_timeout=60000` → Mata transações idle > 60s
- Keepalive previne SSL SYSCALL errors

---

### 3️⃣ HEALTH CHECK ENDPOINT

Adicionar ao `main.py`:

```python
@app.get("/healthz")
async def health_check():
    """Health check com verificação de conexões PostgreSQL"""
    try:
        from database import get_db
        conn = get_db()
        cursor = conn.cursor()
        
        # Verificar conexão
        cursor.execute("SELECT 1")
        
        # Contar conexões ativas
        cursor.execute("""
            SELECT count(*) 
            FROM pg_stat_activity 
            WHERE datname = current_database()
        """)
        connection_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        status = "healthy"
        if connection_count > 45:
            status = "warning"
        
        return {
            "status": status,
            "database": "connected",
            "connections": connection_count,
            "limit": 50
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }, 503
```

**O que faz:**
- Railway pode monitorar a saúde da aplicação
- Alerta se conexões > 45
- Permite debug rápido

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO:

### Passo 1: Adicionar Auto-Cleanup
```bash
# Já criado: auto_cleanup_connections.py
# Falta: Adicionar ao main.py startup
```

### Passo 2: Melhorar database.py
```bash
# Adicionar timeouts ao DB_CONFIG
```

### Passo 3: Health Check
```bash
# Adicionar endpoint /healthz
```

### Passo 4: Deploy
```bash
git add auto_cleanup_connections.py database.py main.py
git commit -m "Add permanent connection cleanup solution"
git push origin main
```

---

## 🎯 RESULTADO ESPERADO:

✅ **Nunca mais** acumulação de conexões mortas
✅ **Auto-limpeza** a cada 5 minutos
✅ **Alertas** quando conexões > 40
✅ **Timeouts** automáticos para queries lentas
✅ **Health check** para monitorização

---

## 🚨 SE VOLTAR A ACONTECER:

Execute o script de emergência:
```bash
python3 emergency_fix.py
```

Ou via Railway Dashboard → PostgreSQL → Query:
```sql
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'railway'
AND state = 'idle'
AND pid != pg_backend_pid();
```

---

**Implementar HOJE para prevenir problemas futuros!**
