# Alternativas Gratuitas ao Render - Hosting e Base de Dados

## 🎯 Requisitos do Projeto

- **Stack:** Python 3.9+, FastAPI/Starlette, Selenium
- **Base de Dados:** PostgreSQL ou SQLite
- **Recursos:** Scraping web (Selenium/Playwright), armazenamento de imagens
- **Tráfego:** Médio (scraping periódico)

---

## 🚀 ALTERNATIVAS DE HOSTING GRATUITAS

### 1. ⭐ **Railway.app** (RECOMENDADO #1)

**Plano Gratuito:**
- ✅ $5 de crédito mensal GRÁTIS (sem cartão de crédito)
- ✅ Deploy automático via GitHub
- ✅ PostgreSQL incluído GRÁTIS
- ✅ Suporte completo a Python/FastAPI
- ✅ Variáveis de ambiente
- ✅ Logs em tempo real
- ✅ SSL automático

**Limitações:**
- ⚠️ $5/mês de crédito (suficiente para apps pequenas/médias)
- ⚠️ Sleep após inatividade (pode configurar cron para manter ativo)

**Compatibilidade com o projeto:** ✅ 100%

**Como migrar:**
```bash
# 1. Criar conta em railway.app
# 2. Conectar GitHub
# 3. New Project > Deploy from GitHub repo
# 4. Adicionar PostgreSQL service
# 5. Configurar variáveis de ambiente
# 6. Deploy automático!
```

**URL:** https://railway.app

---

### 2. ⭐ **Fly.io** (RECOMENDADO #2)

**Plano Gratuito:**
- ✅ Até 3 VMs compartilhadas (256MB RAM cada)
- ✅ 3GB de armazenamento persistente
- ✅ 160GB de tráfego/mês
- ✅ Suporte a Docker (Python/FastAPI)
- ✅ PostgreSQL via extensão
- ✅ SSL automático
- ✅ Deploy via CLI ou GitHub Actions

**Limitações:**
- ⚠️ Requer cartão de crédito (mas não cobra se ficar no free tier)
- ⚠️ 256MB RAM por VM (pode ser pouco para Selenium)
- ⚠️ Configuração mais técnica

**Compatibilidade com o projeto:** ✅ 95% (RAM pode ser limitada para Selenium)

**Como migrar:**
```bash
# 1. Instalar flyctl CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Launch app
fly launch

# 4. Adicionar PostgreSQL
fly postgres create

# 5. Deploy
fly deploy
```

**URL:** https://fly.io

---

### 3. **Vercel** (Para frontend + Serverless)

**Plano Gratuito:**
- ✅ Hosting ilimitado para frontend
- ✅ Serverless Functions (Python)
- ✅ Deploy automático via GitHub
- ✅ SSL automático
- ✅ 100GB de bandwidth/mês

**Limitações:**
- ❌ Não suporta Selenium (timeout de 10s em serverless)
- ❌ Não tem PostgreSQL nativo
- ⚠️ Apenas para APIs stateless simples

**Compatibilidade com o projeto:** ❌ 30% (não suporta Selenium)

**URL:** https://vercel.com

---

### 4. **PythonAnywhere**

**Plano Gratuito:**
- ✅ 1 web app Python
- ✅ 512MB de armazenamento
- ✅ MySQL incluído (não PostgreSQL)
- ✅ Suporte a Flask/FastAPI
- ✅ Sempre ativo (não dorme)

**Limitações:**
- ❌ Não suporta Selenium (sem acesso a browser)
- ❌ Apenas MySQL (não PostgreSQL)
- ⚠️ CPU limitada
- ⚠️ Sem deploy automático via Git

**Compatibilidade com o projeto:** ❌ 40% (sem Selenium, sem PostgreSQL)

**URL:** https://www.pythonanywhere.com

---

### 5. **Koyeb**

**Plano Gratuito:**
- ✅ 1 web service
- ✅ 512MB RAM
- ✅ Deploy via GitHub
- ✅ SSL automático
- ✅ Suporte a Docker

**Limitações:**
- ⚠️ Sem PostgreSQL incluído
- ⚠️ 512MB RAM (limitado para Selenium)
- ⚠️ Sleep após inatividade

**Compatibilidade com o projeto:** ⚠️ 70% (precisa de DB externa)

**URL:** https://www.koyeb.com

---

### 6. **Heroku** (Mudou para pago em 2022)

**Status:** ❌ Não tem mais plano gratuito

---

## 💾 ALTERNATIVAS DE BASE DE DADOS GRATUITAS

### 1. ⭐ **Supabase** (RECOMENDADO #1)

**Plano Gratuito:**
- ✅ PostgreSQL completo
- ✅ 500MB de armazenamento
- ✅ Até 2GB de transferência/mês
- ✅ API REST automática
- ✅ Realtime subscriptions
- ✅ Autenticação incluída
- ✅ Storage para arquivos (1GB)
- ✅ Sem limite de tempo

**Limitações:**
- ⚠️ Pausa após 1 semana de inatividade (reativa automaticamente)
- ⚠️ 500MB de dados

**Como usar:**
```python
# 1. Criar projeto em supabase.com
# 2. Obter connection string
# 3. Usar com SQLAlchemy ou psycopg2

import psycopg2
conn = psycopg2.connect(
    host="db.xxx.supabase.co",
    database="postgres",
    user="postgres",
    password="your-password",
    port=5432
)
```

**URL:** https://supabase.com

---

### 2. ⭐ **Neon** (RECOMENDADO #2)

**Plano Gratuito:**
- ✅ PostgreSQL serverless
- ✅ 3GB de armazenamento
- ✅ Branches ilimitados
- ✅ Sempre ativo (não dorme)
- ✅ Backups automáticos
- ✅ Connection pooling

**Limitações:**
- ⚠️ 3GB de dados
- ⚠️ 100 horas de compute/mês

**Como usar:**
```python
# Connection string direto
DATABASE_URL = "postgresql://user:pass@ep-xxx.neon.tech/dbname"
```

**URL:** https://neon.tech

---

### 3. **ElephantSQL**

**Plano Gratuito:**
- ✅ PostgreSQL 20MB
- ✅ 5 conexões simultâneas
- ✅ Sempre ativo

**Limitações:**
- ⚠️ Apenas 20MB (muito pouco)
- ⚠️ 5 conexões

**URL:** https://www.elephantsql.com

---

### 4. **Aiven**

**Plano Gratuito:**
- ✅ PostgreSQL, MySQL, Redis
- ✅ 1 serviço grátis
- ✅ Backups automáticos

**Limitações:**
- ⚠️ Trial de 30 dias apenas
- ❌ Não é permanentemente gratuito

**URL:** https://aiven.io

---

### 5. **CockroachDB Serverless**

**Plano Gratuito:**
- ✅ PostgreSQL compatível
- ✅ 5GB de armazenamento
- ✅ 250M Request Units/mês
- ✅ Sempre ativo

**Limitações:**
- ⚠️ Sintaxe PostgreSQL mas não 100% compatível
- ⚠️ Pode ter diferenças em queries complexas

**URL:** https://www.cockroachlabs.com

---

## 🏆 RECOMENDAÇÃO FINAL

### ✅ MELHOR COMBINAÇÃO GRATUITA:

**Hosting:** **Railway.app**
- $5 crédito mensal grátis
- PostgreSQL incluído
- Deploy automático
- 100% compatível com o projeto

**OU**

**Hosting:** **Fly.io** + **Base de Dados:** **Supabase**
- Fly.io: 3 VMs grátis
- Supabase: PostgreSQL grátis (500MB)
- Ambos sempre ativos
- 100% compatível

---

## 📊 COMPARAÇÃO RÁPIDA

| Plataforma | Hosting | PostgreSQL | Selenium | Deploy Auto | Sempre Ativo |
|------------|---------|------------|----------|-------------|--------------|
| **Railway** | ✅ Grátis | ✅ Incluído | ✅ Sim | ✅ GitHub | ⚠️ Com cron |
| **Fly.io** | ✅ Grátis | ⚠️ Externo | ⚠️ RAM baixa | ✅ CLI/GitHub | ✅ Sim |
| **Render** | ⚠️ Pago* | ⚠️ Pago* | ✅ Sim | ✅ GitHub | ❌ Sleep |
| **Vercel** | ✅ Grátis | ❌ Não | ❌ Não | ✅ GitHub | ✅ Sim |

*Render mudou para pago em 2023

---

## 🚀 MIGRAÇÃO RECOMENDADA

### Opção 1: Railway (MAIS FÁCIL)

```bash
# 1. Criar conta em railway.app
# 2. New Project > Deploy from GitHub
# 3. Selecionar repositório autoprudente
# 4. Add PostgreSQL service
# 5. Copiar DATABASE_URL para variáveis de ambiente
# 6. Deploy automático!
```

**Tempo estimado:** 15 minutos

---

### Opção 2: Fly.io + Supabase (MAIS RECURSOS)

```bash
# PARTE 1: Supabase (Base de Dados)
# 1. Criar projeto em supabase.com
# 2. Copiar connection string
# 3. Importar dados do Render

# PARTE 2: Fly.io (Hosting)
# 1. Instalar flyctl
# 2. fly launch
# 3. Configurar DATABASE_URL do Supabase
# 4. fly deploy
```

**Tempo estimado:** 30 minutos

---

## 📝 NOTAS IMPORTANTES

1. **Selenium/Scraping:**
   - Railway e Fly.io suportam Selenium
   - Vercel e PythonAnywhere NÃO suportam

2. **PostgreSQL:**
   - Railway inclui PostgreSQL grátis
   - Fly.io precisa de DB externa (Supabase recomendado)

3. **Sempre Ativo:**
   - Railway: Configurar cron job para manter ativo
   - Fly.io: Sempre ativo por padrão
   - Render free tier: Dorme após 15min (problema atual)

4. **Migração de Dados:**
   - Exportar do Render: `pg_dump`
   - Importar para nova DB: `psql` ou interface web

---

## ✅ PRÓXIMOS PASSOS

1. Escolher plataforma (Railway ou Fly.io + Supabase)
2. Criar conta
3. Migrar base de dados
4. Configurar deploy automático
5. Testar scraping
6. Desativar Render

**Queres que te ajude com a migração?**
