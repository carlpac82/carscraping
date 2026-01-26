# 🔐 CONFIGURAÇÃO DE BACKUP AUTOMÁTICO - AUTO PRUDENTE

## 📋 VISÃO GERAL

O sistema de backup automático garante que **NUNCA vais perder dados** do sistema Auto Prudente.

### **O que é feito backup:**
- ✅ Base de dados completa (PostgreSQL/SQLite)
- ✅ Rental Agreements (PDFs)
- ✅ Fotos de inspeções
- ✅ Damage Reports
- ✅ Configurações do sistema

### **Frequência:**
- 🔄 **Semanal** (todos os domingos às 3h da manhã)
- 📦 **Mantém últimos 4 backups** (1 mês de histórico)
- 🗜️ **Compressão automática** (economiza espaço)

---

## 🚀 CONFIGURAÇÃO NO RAILWAY (PRODUÇÃO)

### **Opção 1: Backup Nativo do Railway (RECOMENDADO)**

O Railway já faz backup automático da base de dados PostgreSQL:

1. **Plano Gratuito:**
   - ✅ Backup diário automático
   - ✅ Retenção: 7 dias
   - ✅ Restauração com 1 clique

2. **Plano Pro ($5/mês):**
   - ✅ Backup diário automático
   - ✅ Retenção: 30 dias
   - ✅ Backups sob demanda
   - ✅ Point-in-time recovery

**Como restaurar backup no Railway:**
```bash
# 1. Aceder ao Dashboard do Railway
# 2. Ir para a base de dados PostgreSQL
# 3. Tab "Backups"
# 4. Selecionar backup desejado
# 5. Clicar em "Restore"
```

### **Opção 2: Backup Manual Adicional**

Para ter um backup extra fora do Railway:

#### **1. Instalar script no servidor:**

```bash
# Dar permissões de execução
chmod +x backup_database.py

# Testar backup manual
python3 backup_database.py
```

#### **2. Configurar Cron Job:**

```bash
# Editar crontab
crontab -e

# Adicionar linha (executa todos os domingos às 3h)
0 3 * * 0 cd /app && /usr/bin/python3 backup_database.py >> /app/backup.log 2>&1
```

#### **3. Verificar logs:**

```bash
# Ver logs de backup
tail -f backup.log

# Listar backups criados
ls -lh backups/
```

---

## 💻 CONFIGURAÇÃO LOCAL (DESENVOLVIMENTO)

### **1. Criar diretório de backups:**

```bash
mkdir -p backups
```

### **2. Executar backup manual:**

```bash
python3 backup_database.py
```

### **3. Agendar backup semanal (macOS/Linux):**

```bash
# Editar crontab
crontab -e

# Adicionar linha
0 3 * * 0 cd /Users/filipepacheco/CascadeProjects/carscraping && /usr/bin/python3 backup_database.py
```

---

## 📦 ESTRUTURA DE BACKUPS

```
backups/
├── backup_postgresql_20260126_030000.sql.gz    # Backup BD (comprimido)
├── backup_files_uploads_20260126_030000.tar.gz # Ficheiros uploaded
├── backup_files_static_damage_photos_20260126_030000.tar.gz
└── backup_files_static_inspection_photos_20260126_030000.tar.gz
```

### **Rotação Automática:**
- Mantém **últimos 4 backups semanais** (1 mês)
- Remove automaticamente backups mais antigos
- Economiza espaço em disco

---

## 🔄 RESTAURAR BACKUP

### **PostgreSQL (Railway):**

```bash
# 1. Download do backup
railway db:backup download backup_postgresql_20260126_030000.sql.gz

# 2. Descomprimir
gunzip backup_postgresql_20260126_030000.sql.gz

# 3. Restaurar
psql $DATABASE_URL < backup_postgresql_20260126_030000.sql
```

### **SQLite (Local):**

```bash
# 1. Descomprimir
gunzip backup_sqlite_20260126_030000.db.gz

# 2. Substituir ficheiro atual
cp backup_sqlite_20260126_030000.db autoprudente.db
```

### **Ficheiros (Fotos/PDFs):**

```bash
# Descomprimir e restaurar
tar -xzf backup_files_uploads_20260126_030000.tar.gz -C ./
```

---

## 🔍 VERIFICAÇÃO DE BACKUPS

### **Script de Verificação:**

```python
# verify_backups.py
from pathlib import Path
from datetime import datetime, timedelta

BACKUP_DIR = Path('backups')

# Verificar se existem backups recentes
recent_backups = [
    f for f in BACKUP_DIR.glob('backup_*.gz')
    if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days < 7
]

if recent_backups:
    print(f"✅ {len(recent_backups)} backups recentes encontrados")
    for backup in sorted(recent_backups, key=lambda x: x.stat().st_mtime, reverse=True):
        size_mb = backup.stat().st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"  - {backup.name} ({size_mb:.2f} MB) - {mtime}")
else:
    print("⚠️ ATENÇÃO: Nenhum backup recente encontrado!")
```

---

## 📊 MONITORIZAÇÃO

### **Alertas Recomendados:**

1. **Email se backup falhar** (configurar no script)
2. **Verificação semanal manual** (ver logs)
3. **Teste de restauração mensal** (garantir que backups funcionam)

### **Logs de Backup:**

```bash
# Ver últimos backups
tail -n 50 backup.log

# Procurar erros
grep "ERROR" backup.log

# Verificar espaço em disco
df -h backups/
```

---

## 🛡️ SEGURANÇA DOS BACKUPS

### **Recomendações:**

1. ✅ **Encriptação:** Backups em produção devem ser encriptados
2. ✅ **Armazenamento externo:** Considerar upload para AWS S3 / Google Cloud Storage
3. ✅ **Acesso restrito:** Apenas administradores devem ter acesso
4. ✅ **Teste regular:** Restaurar backup mensalmente para garantir integridade

### **Encriptar Backup (Opcional):**

```bash
# Encriptar com GPG
gpg --symmetric --cipher-algo AES256 backup_postgresql_20260126_030000.sql.gz

# Desencriptar
gpg --decrypt backup_postgresql_20260126_030000.sql.gz.gpg > backup.sql.gz
```

---

## ☁️ BACKUP PARA CLOUD (OPCIONAL)

### **AWS S3:**

```bash
# Instalar AWS CLI
pip install awscli

# Configurar credenciais
aws configure

# Upload automático
aws s3 cp backups/ s3://autoprudente-backups/ --recursive
```

### **Google Cloud Storage:**

```bash
# Instalar gcloud
# https://cloud.google.com/sdk/docs/install

# Upload automático
gsutil -m cp -r backups/ gs://autoprudente-backups/
```

---

## 📞 SUPORTE

### **Em caso de perda de dados:**

1. **NÃO ENTRAR EM PÂNICO** 😌
2. Verificar backups disponíveis: `ls -lh backups/`
3. Escolher backup mais recente
4. Seguir procedimento de restauração acima
5. Verificar integridade dos dados restaurados

### **Contactos:**

- **Railway Support:** https://railway.app/help
- **Documentação:** Ver `AUDIT_REPORT.md`

---

## ✅ CHECKLIST DE CONFIGURAÇÃO

- [ ] Script `backup_database.py` instalado
- [ ] Permissões de execução configuradas (`chmod +x`)
- [ ] Diretório `backups/` criado
- [ ] Backup manual testado com sucesso
- [ ] Cron job configurado (se aplicável)
- [ ] Logs de backup verificados
- [ ] Teste de restauração realizado
- [ ] Railway backups verificados (produção)
- [ ] Documentação lida e compreendida

---

**✅ COM ESTE SISTEMA, OS TEUS DADOS ESTÃO 100% SEGUROS!**

**Última atualização:** 26 Janeiro 2026
