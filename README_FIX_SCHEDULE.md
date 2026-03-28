# Fix para Erro de Schedule Settings

## Problema
Erro: `column "weekday_start_morning" does not exist`

## Solução
Execute o script SQL `fix_commissioners_schedule_columns.sql` na base de dados do Railway:

### Passos:
1. Aceda ao Railway Dashboard
2. Vá ao serviço da base de dados PostgreSQL
3. Clique em "Query" ou "Connect"
4. Execute o conteúdo do ficheiro `fix_commissioners_schedule_columns.sql`

Ou use o comando:
```bash
psql $DATABASE_URL -f fix_commissioners_schedule_columns.sql
```

Este script adiciona as colunas necessárias à tabela `commissioners` para armazenar as configurações de horários.
