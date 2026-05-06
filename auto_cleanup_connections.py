"""
AUTO CLEANUP - Matar conexões idle automaticamente
Adicionar ao main.py para executar a cada 5 minutos
"""

import psycopg2
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import os

def cleanup_idle_connections():
    """Matar conexões idle há mais de 5 minutos"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return
    
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Matar conexões idle há mais de 5 minutos
        cursor.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity 
            WHERE datname = current_database()
            AND state = 'idle'
            AND state_change < NOW() - INTERVAL '5 minutes'
            AND pid != pg_backend_pid();
        """)
        
        killed = cursor.rowcount
        if killed > 0:
            logging.info(f"🧹 Auto-cleanup: killed {killed} idle connections")
        
        # Verificar total de conexões
        cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database();")
        total = cursor.fetchone()[0]
        
        if total > 40:
            logging.warning(f"⚠️  High connection count: {total}/50")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logging.error(f"❌ Auto-cleanup failed: {e}")

def start_connection_cleanup_scheduler():
    """Iniciar scheduler para limpeza automática"""
    scheduler = BackgroundScheduler()
    # Executar a cada 5 minutos
    scheduler.add_job(cleanup_idle_connections, 'interval', minutes=5, id='cleanup_connections')
    scheduler.start()
    logging.info("✅ Connection auto-cleanup scheduler started (every 5 minutes)")
    return scheduler
