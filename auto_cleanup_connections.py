"""
AUTO CLEANUP - Matar conexões idle automaticamente
Adicionar ao main.py para executar a cada 5 minutos
"""

import psycopg2
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import os

def cleanup_idle_connections():
    """
    Matar APENAS conexões verdadeiramente abandonadas
    
    NUNCA mata:
    - Conexões ativas (scraping, inspeções, queries)
    - Conexões idle há menos de 10 minutos
    - Conexões em transação
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return
    
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # SEGURO: Só matar conexões idle há MAIS de 10 minutos
        # E que NÃO estejam em transação (idle in transaction)
        cursor.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity 
            WHERE datname = current_database()
            AND state = 'idle'  -- APENAS idle puro (não "idle in transaction")
            AND state_change < NOW() - INTERVAL '10 minutes'  -- 10 min (era 5)
            AND pid != pg_backend_pid()
            AND application_name NOT LIKE '%psql%'  -- Não matar conexões de admin
            AND application_name NOT LIKE '%pgAdmin%';
        """)
        
        killed = cursor.rowcount
        if killed > 0:
            logging.info(f"🧹 Auto-cleanup: killed {killed} abandoned connections (idle >10min)")
        
        # Verificar total de conexões
        cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database();")
        total = cursor.fetchone()[0]
        
        # Alertar APENAS se muito alto (>45)
        if total > 45:
            logging.warning(f"⚠️  High connection count: {total}/50")
        elif killed > 0:
            logging.info(f"📊 Total connections: {total}/50")
        
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
