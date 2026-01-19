# Backup Full - CarScraping Project
**Data:** 19 Janeiro 2026, 03:44 UTC

## 📦 Conteúdo do Backup

Este backup inclui:

### 1. **Código Fonte** (`/code`)
- Todos os ficheiros Python (`.py`)
- Lógica de negócio, rotas API, processamento de dados

### 2. **Ficheiros Estáticos** (`/static`)
- Imagens promocionais (image003.png - image010.png)
- Logotipo (ap-heather.png)
- PDFs dos Termos e Condições (PT, EN, FR)
- Ficheiros CSS e JavaScript

### 3. **Templates** (`/templates`)
- Templates HTML para emails (PT, EN, FR)
- Templates de páginas web
- Dashboards e formulários

### 4. **Configurações**
- `requirements.txt` - Dependências Python
- `railway.json` - Configuração Railway
- `.gitignore` - Ficheiros ignorados pelo Git
- `README.md` - Documentação do projeto

### 5. **Base de Dados** (`/database`)
- ⚠️ **Nota:** Dump PostgreSQL não incluído neste backup automático
- Para fazer backup da BD do Railway, execute:
  ```bash
  python3 backup_database_railway.py
  ```
- Ou manualmente:
  ```bash
  export DATABASE_URL="postgresql://..."
  pg_dump $DATABASE_URL > backups/database/railway_postgres_YYYYMMDD_HHMMSS.sql
  ```

## 📊 Estatísticas

- **Tamanho Total:** 153 MB (comprimido)
- **Ficheiros:** Código + Static + Templates + Config
- **Formato:** tar.gz

## 🔄 Como Restaurar

1. **Extrair backup:**
   ```bash
   cd backups
   tar -xzf backup_full_20260119_034407.tar.gz
   ```

2. **Restaurar código:**
   ```bash
   cp -r backup_full_20260119_034407/code/* ../
   cp -r backup_full_20260119_034407/static/* ../static/
   cp -r backup_full_20260119_034407/templates/* ../templates/
   ```

3. **Restaurar base de dados:**
   ```bash
   psql $DATABASE_URL < backups/database/railway_postgres_YYYYMMDD_HHMMSS.sql
   ```

## 🛠️ Scripts de Backup

- **`create_full_backup.sh`** - Backup automático completo
- **`backup_database_railway.py`** - Backup da BD PostgreSQL do Railway

## 📝 Informações do Sistema

Ver ficheiro `backup_info.txt` dentro do backup para:
- Data e hora do backup
- Branch e commit Git
- Hostname e utilizador
- Estado do repositório
