BACKUP COMPLETO - 20260111_172733
================================

Este backup contém:

✅ Código Fonte:
   - main.py (FastAPI backend)
   - database.py (conexão PostgreSQL)
   - requirements.txt (dependências Python)
   - .env (variáveis de ambiente)
   - railway.json (configuração Railway)

✅ Templates:
   - Todos os ficheiros HTML (index.html, price_automation.html, etc.)

✅ Static:
   - Todas as fotos dos carros (grupos B1, B2, C, D, E1, E2, etc.)
   - Favicon e outros assets

✅ Uploads:
   - Ficheiros CSV/Excel carregados

✅ Base de Dados PostgreSQL:
   Para exportar manualmente se necessário:
   railway run pg_dump --no-owner --no-acl > database_export.sql

Data do Backup: 11/01/2026 às 17:27:33
Commit Git: 7ee68f9 (FIX: Adicionar persistência ao deletePeriod)

Funcionalidades incluídas neste backup:
- Múltiplos períodos por mês funcionando
- Eliminação de períodos com persistência
- Upload CSV mantém período selecionado
- Popup clean para atualizar Current Prices do Automated Prices
- Todos os grupos de carros (incluindo K e Comerciais)

Para restaurar:
1. Copiar ficheiros para diretório do projeto
2. Instalar dependências: pip install -r requirements.txt
3. Restaurar base de dados: railway run psql < database_export.sql
4. Deploy: git push origin main
