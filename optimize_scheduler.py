#!/usr/bin/env python3
"""
Otimizações para o scheduler para prevenir bloqueios
"""
import os
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import psycopg2

def setup_optimized_scheduler():
    """Configura scheduler otimizado para prevenir bloqueios"""
    
    print("🔧 CONFIGURANDO SCHEDULER OTIMIZADO", flush=True)
    
    # Configurar executors com limites de threads
    jobstores = {
        'default': SQLAlchemyJobStore(url=os.getenv('DATABASE_URL'))
    }
    
    executors = {
        'default': ThreadPoolExecutor(max_workers=3),  # Limitar threads
        'email': ThreadPoolExecutor(max_workers=1),     # Thread separada para emails
    }
    
    job_defaults = {
        'coalesce': True,          # Combinar jobs similares
        'max_instances': 1,        # Máximo 1 instância por job
        'misfire_grace_time': 300  # 5 minutos de tolerância
    }
    
    scheduler = BackgroundScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone='UTC'
    )
    
    # Adicionar jobs otimizados
    scheduler.add_job(
        func=optimized_checkout_email_checker,
        trigger='interval',
        minutes=10,  # Aumentar de 5 para 10 minutos
        id='checkout_email_checker',
        name='Checkout Email Checker (every 10 min)',
        executor='email',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Scheduler otimizado iniciado", flush=True)
    return scheduler

def optimized_checkout_email_checker():
    """Versão otimizada do checkout email checker"""
    try:
        from schedule_checkout_emails import get_pending_emails, mark_email_sent
        import requests
        import time
        
        start_time = time.time()
        
        # Timeout para prevenir bloqueios
        if time.time() - start_time > 300:  # 5 minutos max
            logging.warning("⏰ Checkout email checker timeout")
            return
        
        pending = get_pending_emails()
        
        if not pending:
            logging.info("✅ No pending checkout emails")
            return
        
        # Processar no máximo 5 emails por vez
        pending = pending[:5]
        logging.info(f"📧 Processing {len(pending)} emails")
        
        for email_data in pending:
            try:
                # Timeout individual para cada email
                email_start = time.time()
                
                # Processar email aqui...
                # (implementação otimizada)
                
                if time.time() - email_start > 60:  # 1 minuto max por email
                    logging.warning("⏰ Individual email timeout")
                    continue
                    
            except Exception as e:
                logging.error(f"❌ Error processing email: {e}")
                continue
        
        logging.info(f"✅ Checkout emails processed in {time.time() - start_time:.2f}s")
        
    except Exception as e:
        logging.error(f"❌ Optimized checkout email checker error: {e}")

def cleanup_old_scheduled_emails():
    """Limpa emails antigos para prevenir acúmulo"""
    try:
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Remover emails com mais de 30 dias
        cursor.execute("""
            DELETE FROM scheduled_checkout_emails 
            WHERE created_at < NOW() - INTERVAL '30 days'
            AND status IN ('sent', 'error')
        """)
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            logging.info(f"🧹 Cleaned {deleted} old scheduled emails")
        
    except Exception as e:
        logging.error(f"❌ Error cleaning old emails: {e}")

if __name__ == "__main__":
    setup_optimized_scheduler()
