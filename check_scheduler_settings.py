#!/usr/bin/env python3
"""
Verificar configurações do scheduler na base de dados
"""
import os
import json
import psycopg2

def check_settings():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("\n" + "="*80)
        print("🔍 VERIFICANDO CONFIGURAÇÕES DO SCHEDULER")
        print("="*80 + "\n")
        
        # Verificar automatedReportsAdvanced
        cursor.execute("""
            SELECT setting_key, setting_value 
            FROM price_automation_settings 
            WHERE setting_key = 'automatedReportsAdvanced'
        """)
        row = cursor.fetchone()
        
        if row:
            key, value = row
            print(f"✅ Encontrado: {key}")
            print(f"\n📋 Valor guardado:")
            print("="*80)
            
            settings = json.loads(value)
            print(json.dumps(settings, indent=2))
            
            print("\n" + "="*80)
            print("📊 ANÁLISE:")
            print("="*80)
            
            # Verificar DAILY
            daily = settings.get('daily', {})
            daily_enabled = daily.get('enabled', False)
            print(f"\n📅 DAILY:")
            print(f"   Enabled: {daily_enabled}")
            if daily_enabled:
                schedules = daily.get('schedules', [])
                print(f"   Schedules: {len(schedules)}")
                for idx, schedule in enumerate(schedules):
                    print(f"\n   Schedule #{idx + 1}:")
                    print(f"      Search Time: {schedule.get('searchTime')}")
                    print(f"      Send Time: {schedule.get('sendTime')}")
                    print(f"      Days: {schedule.get('days')}")
                    print(f"      Locations: {schedule.get('locations')}")
            
            # Verificar WEEKLY
            weekly = settings.get('weekly', {})
            weekly_enabled = weekly.get('enabled', False)
            print(f"\n📆 WEEKLY:")
            print(f"   Enabled: {weekly_enabled}")
            if weekly_enabled:
                print(f"   Day: {weekly.get('day')}")
                print(f"   Search Time: {weekly.get('searchTime')}")
                print(f"   Send Time: {weekly.get('sendTime')}")
                print(f"   Days: {weekly.get('days')}")
                print(f"   Locations: {weekly.get('locations')}")
            
            # Verificar MONTHLY
            monthly = settings.get('monthly', {})
            monthly_enabled = monthly.get('enabled', False)
            print(f"\n📊 MONTHLY:")
            print(f"   Enabled: {monthly_enabled}")
            if monthly_enabled:
                print(f"   Day: {monthly.get('day')}")
                print(f"   Search Time: {monthly.get('searchTime')}")
                print(f"   Send Time: {monthly.get('sendTime')}")
                print(f"   Days: {monthly.get('days')}")
                print(f"   Locations: {monthly.get('locations')}")
            
            print("\n" + "="*80)
            
            # CONCLUSÃO
            if daily_enabled or weekly_enabled or monthly_enabled:
                print("⚠️  PROBLEMA ENCONTRADO!")
                print("="*80)
                print("Há tarefas ATIVAS no scheduler mesmo com toggles OFF na interface!")
                print("\nPossível causa:")
                print("- A base de dados tem valores antigos que não foram atualizados")
                print("- A interface não está a guardar corretamente quando desativas")
                print("\nSolução:")
                print("1. Desativar todos os relatórios na interface")
                print("2. Clicar em 'Guardar Configurações'")
                print("3. Verificar se os valores foram atualizados na BD")
            else:
                print("✅ TUDO OK - Nenhuma tarefa ativa")
        else:
            print("📭 Nenhuma configuração encontrada na base de dados")
            print("   (Isto é normal se nunca configuraste relatórios automáticos)")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_settings()
