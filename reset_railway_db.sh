#!/bin/bash
# Script para limpar PostgreSQL do Railway

echo "🔄 LIMPAR BASE DE DADOS RAILWAY"
echo "================================"
echo ""

# Verificar se psql está instalado
if ! command -v psql &> /dev/null; then
    echo "❌ psql não encontrado!"
    echo "Instala PostgreSQL client:"
    echo "  macOS: brew install postgresql"
    exit 1
fi

echo "📋 Precisas da DATABASE_URL do Railway PostgreSQL"
echo ""
echo "Onde encontrar:"
echo "1. Railway > Postgres service > Connect tab > Public Network"
echo "2. Copia a 'Connection URL' completa"
echo ""

# Pedir DATABASE_URL
read -p "Cola a DATABASE_URL: " DATABASE_URL

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL não pode estar vazia!"
    exit 1
fi

echo ""
echo "⚠️  ATENÇÃO: Isto vai APAGAR TODAS as tabelas!"
read -p "Tens certeza? (sim/não): " confirm

if [ "$confirm" != "sim" ]; then
    echo "❌ Cancelado pelo utilizador"
    exit 0
fi

echo ""
echo "🔄 Limpando base de dados..."
echo ""

# Executar SQL de limpeza
psql "$DATABASE_URL" << EOF
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Base de dados limpa com sucesso!"
    echo ""
    echo "Próximo passo:"
    echo "1. Ir para Railway > carscraping service"
    echo "2. Deployments tab > ⋮ > Redeploy"
    echo "3. Aguardar deploy completar"
else
    echo ""
    echo "❌ Erro ao limpar base de dados!"
    exit 1
fi
