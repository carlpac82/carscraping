#!/usr/bin/env python3
"""
Script para diagnosticar problemas com o scheduler e identificar causas de bloqueio
"""
import os
import sys
import time
import threading
import logging
from datetime import datetime
import psycopg2
from urllib.parse import urlparse

def diagnose_scheduler_issues():
    """Diagnostica possíveis problemas com o scheduler"""
    
    print("=" * 80)
    print("🔍 DIAGNÓSTICO DO SCHEDULER E BLOQUEIOS")
    print("=" * 80)
    
    # 1. Verificar configuração do scheduler
    print("\n1. 📊 CONFIGURAÇÃO DO SCHEDULER:")
    try:
        from automated_scheduler import scheduler
        
        if scheduler is None:
            print("❌ Scheduler não inicializado")
            return False
        
        print(f"✅ Scheduler ativo: {scheduler.running}")
        print(f"✅ Jobs ativos: {len(scheduler.get_jobs())}")
        
        # Verificar se há jobs longos
        for job in scheduler.get_jobs():
            print(f"   - {job.name}: {job.id}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar scheduler: {e}")
    
    # 2. Verificar conexões à base de dados
    print("\n2. 🔌 CONEXÕES À BASE DE DADOS:")
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL não encontrada")
            return False
        
        # Testar conexão
        start_time = time.time()
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar se há conexões bloqueadas
        cursor.execute("""
            SELECT state, count(*) 
            FROM pg_stat_activity 
            WHERE datname = current_database()
            GROUP BY state
        """)
        connections = cursor.fetchall()
        
        print(f"✅ Conexão testada em {time.time() - start_time:.2f}s")
        print("📊 Estado das conexões:")
        for state, count in connections:
            print(f"   - {state}: {count}")
        
        # Verificar queries longas
        cursor.execute("""
            SELECT query, state, now() - query_start AS duration
            FROM pg_stat_activity 
            WHERE datname = current_database()
            AND state = 'active'
            AND now() - query_start > interval '30 seconds'
        """)
        long_queries = cursor.fetchall()
        
        if long_queries:
            print(f"⚠️ {len(long_queries)} queries longas (>30s):")
            for query, state, duration in long_queries:
                print(f"   - {duration}: {query[:100]}...")
        else:
            print("✅ Nenhuma query longa detectada")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro na base de dados: {e}")
    
    # 3. Verificar threads ativos
    print("\n3. 🧵 THREADS ATIVOS:")
    try:
        threads = threading.enumerate()
        print(f"✅ Threads ativos: {len(threads)}")
        
        for thread in threads[:10]:  # Mostrar apenas as primeiras 10
            print(f"   - {thread.name}: {thread.ident}")
        
        if len(threads) > 50:
            print(f"⚠️ Muitas threads ativas ({len(threads)}), possível leak")
        
    except Exception as e:
        print(f"❌ Erro ao verificar threads: {e}")
    
    # 4. Verificar memória
    print("\n4. 💾 USO DE MEMÓRIA:")
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        print(f"✅ RSS: {memory_info.rss / 1024 / 1024:.1f} MB")
        print(f"✅ VMS: {memory_info.vms / 1024 / 1024:.1f} MB")
        print(f"✅ CPU: {process.cpu_percent():.1f}%")
        
        if memory_info.rss / 1024 / 1024 > 500:
            print("⚠️ Alto uso de memória detectado")
        
    except ImportError:
        print("⚠️ psutil não disponível para verificar memória")
    except Exception as e:
        print(f"❌ Erro ao verificar memória: {e}")
    
    # 5. Verificar emails pendentes
    print("\n5. 📧 EMAILS PENDENTES:")
    try:
        from schedule_checkout_emails import get_pending_emails
        
        start_time = time.time()
        pending = get_pending_emails()
        duration = time.time() - start_time
        
        print(f"✅ {len(pending)} emails pendentes (verificado em {duration:.2f}s)")
        
        if len(pending) > 10:
            print("⚠️ Muitos emails pendentes, pode causar lentidão")
        
        if duration > 5:
            print("⚠️ Query de emails demorou muito tempo")
        
    except Exception as e:
        print(f"❌ Erro ao verificar emails pendentes: {e}")
    
    # 6. Verificar locks na base de dados
    print("\n6. 🔒 LOCKS NA BASE DE DADOS:")
    try:
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.relname AS table_name, l.locktype, l.mode
            FROM pg_locks l
            JOIN pg_class t ON l.relation = t.oid
            WHERE NOT l.granted
        """)
        waiting_locks = cursor.fetchall()
        
        if waiting_locks:
            print(f"⚠️ {len(waiting_locks)} locks em espera:")
            for table, locktype, mode in waiting_locks:
                print(f"   - {table}: {locktype} ({mode})")
        else:
            print("✅ Nenhum lock em espera")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar locks: {e}")
    
    print("\n" + "=" * 80)
    print("🔍 DIAGNÓSTICO CONCLUÍDO")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    diagnose_scheduler_issues()
