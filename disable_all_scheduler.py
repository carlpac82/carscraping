#!/usr/bin/env python3
"""
DESATIVAR TODAS AS CONFIGURAÇÕES DO SCHEDULER
Este script garante que NENHUMA tarefa automática está ativa
"""
import os
import json
import psycopg2

def disable_all_scheduler_tasks():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        print("   Set it with: export DATABASE_URL='your_railway_postgres_url'")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("\n" + "="*80)
        print("🛑 DESATIVANDO TODAS AS TAREFAS DO SCHEDULER")
        print("="*80 + "\n")
        
        # Criar configuração com TUDO desativado
        disabled_config = {
            "daily": {
                "enabled": False,
                "schedules": []
            },
            "weekly": {
                "enabled": False,
                "day": "saturday",
                "searchTime": "09:55",
                "sendTime": "10:00",
                "days": [7, 14, 30],
                "locations": {
                    "albufeira": False,
                    "faro": False
                }
            },
            "monthly": {
                "enabled": False,
                "day": "1",
                "searchTime": "09:55",
                "sendTime": "10:00",
                "days": [7, 14, 30, 60],
                "locations": {
                    "albufeira": False,
                    "faro": False
                },
                "period": 6
            }
        }
        
        # Verificar se já existe
        cursor.execute("""
            SELECT setting_value 
            FROM price_automation_settings 
            WHERE setting_key = 'automatedReportsAdvanced'
        """)
        row = cursor.fetchone()
        
        if row:
            print("📋 Configuração existente encontrada")
            old_config = json.loads(row[0])
            print(f"\n   Daily enabled: {old_config.get('daily', {}).get('enabled', False)}")
            print(f"   Weekly enabled: {old_config.get('weekly', {}).get('enabled', False)}")
            print(f"   Monthly enabled: {old_config.get('monthly', {}).get('enabled', False)}")
            
            # UPDATE
            cursor.execute("""
                UPDATE price_automation_settings 
                SET setting_value = %s 
                WHERE setting_key = 'automatedReportsAdvanced'
            """, (json.dumps(disabled_config),))
            
            print("\n✅ Configuração ATUALIZADA para DESATIVADO")
        else:
            print("📭 Nenhuma configuração existente")
            
            # INSERT
            cursor.execute("""
                INSERT INTO price_automation_settings (setting_key, setting_value)
                VALUES ('automatedReportsAdvanced', %s)
            """, (json.dumps(disabled_config),))
            
            print("✅ Configuração CRIADA como DESATIVADO")
        
        conn.commit()
        
        # Verificar resultado
        cursor.execute("""
            SELECT setting_value 
            FROM price_automation_settings 
            WHERE setting_key = 'automatedReportsAdvanced'
        """)
        row = cursor.fetchone()
        
        if row:
            final_config = json.loads(row[0])
            print("\n" + "="*80)
            print("✅ VERIFICAÇÃO FINAL:")
            print("="*80)
            print(f"   Daily enabled: {final_config.get('daily', {}).get('enabled', False)}")
            print(f"   Weekly enabled: {final_config.get('weekly', {}).get('enabled', False)}")
            print(f"   Monthly enabled: {final_config.get('monthly', {}).get('enabled', False)}")
            
            all_disabled = (
                not final_config.get('daily', {}).get('enabled', False) and
                not final_config.get('weekly', {}).get('enabled', False) and
                not final_config.get('monthly', {}).get('enabled', False)
            )
            
            if all_disabled:
                print("\n✅ SUCESSO! Todas as tarefas estão DESATIVADAS")
                print("   O scheduler não vai executar NENHUMA pesquisa automática")
            else:
                print("\n⚠️  ATENÇÃO! Ainda há tarefas ativas!")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        print("🔄 PRÓXIMO PASSO:")
        print("="*80)
        print("1. Reiniciar o servidor Railway para aplicar as mudanças")
        print("2. Verificar logs para confirmar que não há mais pesquisas automáticas")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    disable_all_scheduler_tasks()
