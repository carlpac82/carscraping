#!/bin/bash

echo "🚀 MIGRAÇÃO RÁPIDA: RENDER → RAILWAY"
echo "===================================================="

RENDER_URL="postgresql://carrental_user:cmXcauHIuQinAyDQjcB9XiVMU0Gaxviz@dpg-d44gvnm3jp1c73dc2edg-a.frankfurt-postgres.render.com/carrental_db_9klo"
RAILWAY_URL="postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

echo ""
echo "📥 Exportando dados do Render..."
pg_dump "$RENDER_URL" \
  --data-only \
  --no-owner \
  --no-privileges \
  --disable-triggers \
  --table=recent_searches \
  --table=automated_search_history \
  --table=automated_price_rules \
  --table=system_logs \
  --table=whatsapp_config \
  --table=whatsapp_contacts \
  --table=whatsapp_conversations \
  --table=whatsapp_quick_replies \
  --table=whatsapp_templates \
  --table=oauth_tokens \
  --table=damage_reports \
  --table=damage_report_templates \
  --table=damage_report_coordinates \
  --table=damage_report_mapping_history \
  --table=rental_agreement_templates \
  --table=rental_agreement_coordinates \
  --table=rental_agreement_mapping_history \
  --table=vehicle_inspections \
  --table=inspection_photos \
  --table=vehicle_photos \
  --table=vehicle_images \
  --table=vehicle_name_overrides \
  --table=downloads_history \
  > /tmp/render_data.sql

if [ $? -eq 0 ]; then
    echo "✅ Dados exportados para /tmp/render_data.sql"
    echo ""
    echo "📤 Importando para Railway..."
    
    psql "$RAILWAY_URL" < /tmp/render_data.sql
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "===================================================="
        echo "✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!"
        echo "===================================================="
        echo ""
        echo "🌐 Acede: https://carscraping.up.railway.app"
        echo "🔐 Login: mesmas credenciais do Render"
        echo ""
        echo "Dados migrados:"
        echo "  ✅ Histórico de pesquisas"
        echo "  ✅ Configurações"
        echo "  ✅ Fotos dos carros"
        echo "  ✅ Damage Reports"
        echo "  ✅ Logs do sistema"
        echo "  ✅ Tudo!"
        echo ""
        rm /tmp/render_data.sql
    else
        echo "❌ Erro ao importar para Railway"
        exit 1
    fi
else
    echo "❌ Erro ao exportar do Render"
    exit 1
fi
